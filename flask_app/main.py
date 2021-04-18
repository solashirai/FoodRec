from flask import Flask, request, abort
import rdflib
from food_rec.services.food import (
    RemoteGraphFoodKgQueryService,
    LocalGraphFoodKgQueryService,
    RecipeEmbeddingService,
)
from food_rec.services.user import (
    RemoteGraphUserKgQueryService,
    LocalGraphUserKgQueryService,
)
from food_rec.services.guideline import LocalGraphGuidelineKgQueryService
from food_rec.services import (
    GraphIngredientSubstitutionService,
    GraphExplainableFoodRecommenderService,
)
from food_rec.services.exceptions import NotFoundException, MalformedContentException
from food_rec.utils.path import DATA_DIR


recipe_ns = rdflib.Namespace("http://idea.rpi.edu/heals/kb/recipe/")


def create_app(*, TESTING=False):

    app = Flask(__name__)

    user_files = tuple(
        (DATA_DIR / file).resolve()
        for file in ["user_example.trig", "diet_restrictions.trig"]
    )
    USERKG_SHARED = LocalGraphUserKgQueryService(file_paths=user_files)

    if TESTING:
        # for testing locally
        food_kg_files = tuple(
            (DATA_DIR / file).resolve()
            for file in [
                "food_kg_test_dataset.trig",
                "simplified_test_usda.ttl",
                "foodon_total.trig",
                "food_kg_test_precomputed_nutrition.ttl",
                "manual_ingredient_substitution_sets.trig",
            ]
        )

        FOODKG_SHARED = LocalGraphFoodKgQueryService(file_paths=food_kg_files)

        RECIPE_EMBEDDINGS = RecipeEmbeddingService(
            id_file=(DATA_DIR / "food_kg_embeddings" / "testfoodkg_id.pkl").resolve(),
            embedding_file=(
                DATA_DIR / "food_kg_embeddings" / "testfoodkg_emb.pkl"
            ).resolve(),
        )
    else:
        FOODKG_SHARED = RemoteGraphFoodKgQueryService(
            sparql_endpoint="http://localhost:9999/blazegraph/sparql"  # "http://twks-server:8080/sparql/assertions"
        )
        # USERKG_SHARED = RemoteGraphUserKgQueryService(
        #     sparql_endpoint="http://localhost:9999/blazegraph/sparql"#"http://twks-server:8080/sparql/assertions"
        # )
        RECIPE_EMBEDDINGS = RecipeEmbeddingService(
            id_file=(DATA_DIR / "food_kg_embeddings" / "5k_foodkg_id.pkl").resolve(),
            embedding_file=(
                DATA_DIR / "food_kg_embeddings" / "5k_foodkg_emb.pkl"
            ).resolve(),
        )

    FOOD_SUBS = GraphIngredientSubstitutionService(
        food_kg=FOODKG_SHARED, user_kg=USERKG_SHARED
    )

    # TODO: cleanup of how guidelineKG and recipe embedding service are set up
    guideline_files = tuple(
        (DATA_DIR / file).resolve() for file in ["heals-guidelines.owl"]
    )
    GUIDELINEKG_SHARED = LocalGraphGuidelineKgQueryService(file_paths=guideline_files)

    FOOD_REC = GraphExplainableFoodRecommenderService(
        food_kg=FOODKG_SHARED,
        user_kg=USERKG_SHARED,
        guideline_kg=GUIDELINEKG_SHARED,
        recipe_embedding_service=RECIPE_EMBEDDINGS,
    )

    @app.route("/")
    def hello_world():
        return "Hello, World!"

    @app.route("/recipe_subs", methods=["GET"])
    def get_subs_for_recipe():
        args = request.args
        recipe_uri_part = args["recipe_uri"]
        recipe_uri = rdflib.URIRef(recipe_uri_part)

        try:
            recipe = FOODKG_SHARED.get_recipe_by_uri(recipe_uri=recipe_uri)
            allsubs = FOOD_SUBS.get_substitutions_for_recipe(recipe=recipe, user=None)
            app.logger.info(f"retrieved substitutes for recipe {recipe.name}")

            allsubs = [
                {
                    "fromIngredient": sub.from_ing.uri,
                    "toIngredient": sub.to_ing.uri,
                    "explanation": sub.explanation,
                }
                for sub in allsubs
            ]

            return {"substitution_options": allsubs}

        except NotFoundException as e:
            abort(404, description=e)
        except MalformedContentException as e:
            abort(500, description=e)

    @app.route("/recipe_user_subs", methods=["GET"])
    def get_subs_for_recipe_and_user():
        args = request.args
        user_uri_part = args["user_uri"]
        user_uri = rdflib.URIRef(user_uri_part)

        recipe_uri_part = args["recipe_uri"]
        recipe_uri = rdflib.URIRef(recipe_uri_part)

        try:
            recipe = FOODKG_SHARED.get_recipe_by_uri(recipe_uri=recipe_uri)
            user = USERKG_SHARED.get_user_by_uri(user_uri=user_uri)
            allsubs = FOOD_SUBS.get_substitutions_for_recipe(recipe=recipe, user=user)
            app.logger.info(
                f"retrieved substitutes for recipe {recipe.name} for user {user.name}"
            )

            allsubs = [
                {
                    "fromIngredient": sub.from_ing.uri,
                    "toIngredient": sub.to_ing.uri,
                    "explanation": sub.explanation,
                }
                for sub in allsubs
            ]
            return {"substitution_options": allsubs}
        except NotFoundException as e:
            abort(404, description=e)
        except MalformedContentException as e:
            abort(500, description=e)

    @app.route("/user_info", methods=["GET"])
    def get_user_info():
        args = request.args
        user_uri_part = args["user_uri"]
        # /user_info?user_uri=http%3A%2F%2Fidea.rpi.edu%2Fheals%2Fkb%2Fuser%2Fuser_id%2FUSER_001
        user_uri = rdflib.URIRef(user_uri_part)

        try:
            user = USERKG_SHARED.get_user_by_uri(user_uri=user_uri)

            user_info = user.to_dict()

            return user_info
        except NotFoundException as e:
            abort(404, description=e)
        except MalformedContentException as e:
            abort(500, description=e)

    @app.route("/user_mealplan_rec", methods=["GET"])
    def get_mealplan_for_user():
        args = request.args
        user_uri_part = args["user_uri"]
        # /user_mealplan_rec?user_uri=http%3A%2F%2Fidea.rpi.edu%2Fheals%2Fkb%2Fuser%2Fuser_id%2FUSER_001

        user_uri = rdflib.URIRef(user_uri_part)

        days = int(args.get("days", 3))
        meal_per_day = int(args.get("meals_per_day", 2))

        try:
            user = USERKG_SHARED.get_user_by_uri(user_uri=user_uri)
            mealplan_cand = FOOD_REC.get_meal_plan_for_user(
                user=user, number_of_days=days, meals_per_day=meal_per_day
            )
            mealplan = mealplan_cand.domain_object

            mp_days = [
                {
                    "meals": [
                        {
                            "recipe_name": recipe_rec.recipe.name,
                            "explanation": recipe_rec.explanation,
                            "ingredients": [
                                ing.label for ing in recipe_rec.recipe.ingredient_set
                            ],
                            "calories(kcal)": recipe_rec.recipe.total_nutritional_info.energ__kcal,
                            "sodium(mg)": recipe_rec.recipe.total_nutritional_info.sodium_mg,
                            "carbohydrates(g)": recipe_rec.recipe.total_nutritional_info.carbohydrt_g,
                        }
                        for recipe_rec in day.recipe_recommendations
                    ],
                    "day_explanation": day.explanation,
                }
                for day in mealplan.meal_plan_days
            ]
            return {
                "mealplan_days": mp_days,
                "overall_explanation": mealplan.explanation,
                "context_username": mealplan_cand.context.target_user.name,
                "context_user_favorite_recipes": [
                    FOODKG_SHARED.get_recipe_by_uri(recipe_uri=ru).name
                    for ru in mealplan_cand.context.target_user.favorite_recipe_uri_set
                ],
            }
        except NotFoundException as e:
            abort(404, description=e)
        except MalformedContentException as e:
            abort(500, description=e)

    return app


app = create_app(TESTING=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
