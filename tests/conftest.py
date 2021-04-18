import pytest
import rdflib
from rdflib import Namespace

from food_rec.utils.path import *
from food_rec.services import *
from food_rec.models import *
from food_rec.utils import cfg

from frex import Explanation, ConstraintType

FIVETHOUSAND_RECIPES_REMOTE = False

ingredient_ns = Namespace("http://idea.rpi.edu/heals/kb/ingredientname/")
recipe_ns = Namespace("http://idea.rpi.edu/heals/kb/recipe/")
food_kg_files = (
    (DATA_DIR / file).resolve()
    for file in [
        "food_kg_test_dataset.trig",
        "simplified_test_usda.ttl",
        "food_kg_test_precomputed_nutrition.ttl",
        "foodon_total.trig",
        "manual_ingredient_substitution_sets.trig",
    ]
)
user_files = (
    (DATA_DIR / file).resolve()
    for file in ["user_example.trig", "diet_restrictions.trig"]
)
guideline_files = [(DATA_DIR / file).resolve() for file in ["heals-guidelines.owl"]]


@pytest.fixture(scope="session")
def food_kg() -> LocalGraphFoodKgQueryService:
    if FIVETHOUSAND_RECIPES_REMOTE:
        f = RemoteGraphFoodKgQueryService(
            sparql_endpoint="http://localhost:9999/blazegraph/sparql"
        )  #
    else:
        f = LocalGraphFoodKgQueryService(file_paths=food_kg_files)
    return f


@pytest.fixture(scope="session")
def embedding_service() -> RecipeEmbeddingService:
    if FIVETHOUSAND_RECIPES_REMOTE:
        return RecipeEmbeddingService(
            id_file=(DATA_DIR / "food_kg_embeddings" / "5k_foodkg_id.pkl").resolve(),
            embedding_file=(
                DATA_DIR / "food_kg_embeddings" / "5k_foodkg_emb.pkl"
            ).resolve(),
        )

    else:
        return RecipeEmbeddingService(
            id_file=(DATA_DIR / "food_kg_embeddings" / "testfoodkg_id.pkl").resolve(),
            embedding_file=(
                DATA_DIR / "food_kg_embeddings" / "testfoodkg_emb.pkl"
            ).resolve(),
        )


@pytest.fixture(scope="session")
def user_kg() -> LocalGraphUserKgQueryService:
    u = LocalGraphUserKgQueryService(file_paths=user_files)
    return u


@pytest.fixture(scope="session")
def guideline_kg() -> LocalGraphGuidelineKgQueryService:
    g = LocalGraphGuidelineKgQueryService(file_paths=guideline_files)
    return g


@pytest.fixture(scope="session")
def food_kg_subs(food_kg, user_kg) -> GraphIngredientSubstitutionService:
    s = GraphIngredientSubstitutionService(food_kg=food_kg, user_kg=user_kg)
    return s


@pytest.fixture(scope="session")
def food_kg_rec(
    food_kg, user_kg, guideline_kg, embedding_service
) -> GraphExplainableFoodRecommenderService:
    s = GraphExplainableFoodRecommenderService(
        food_kg=food_kg,
        user_kg=user_kg,
        guideline_kg=guideline_kg,
        recipe_embedding_service=embedding_service,
    )
    return s


@pytest.fixture(scope="session")
def potato_nutrition():
    return NutritionInfo(
        shrt__desc="POTATOES,HASH BROWN,HOME-PREPARED",
        gm_wt__desc1="1 cup",
        folate__tot_micro_g=16,
        vit__c_mg=13,
        vit__b6_mg=0.472,
        food__folate_micro_g=16,
        thiamin_mg=0.172,
        phosphorus_mg=70,
        cholestrl_mg=0,
        lipid__tot_g=12.52,
        gm_wt_1=156,
        folate__d_f_e_micro_g=16,
        sodium_mg=342,
        ash_g=2.12,
        f_a__sat_g=1.883,
        carbohydrt_g=35.11,
        lut__zea__micro_g=16,
        choline__tot__mg=23.2,
        protein_g=3,
        water_g=47.25,
        niacin_mg=2.302,
        magnesium_mg=35,
        f_a__mono_g=5.299,
        iron_mg=0.55,
        beta__carot_micro_g=3,
        manganese_mg=0.247,
        vit__k_micro_g=3.7,
        fiber__t_d_g=3.2,
        potassium_mg=576,
        selenium_micro_g=0.5,
        copper_mg=0.293,
        riboflavin_mg=0.033,
        calcium_mg=14,
        panto__acid_mg=0.893,
        zinc_mg=0.47,
        sugar__tot_g=1.49,
        vit__e_mg=0.01,
        energ__kcal=265,
        f_a__poly_g=4.703,
        vit__a__i_u=5,
    )


@pytest.fixture(scope="session")
def potato_ing(food_kg, test_ingredient_vars):
    return food_kg.get_ingredient_by_uri(ing_uri=test_ingredient_vars.potato_uri)


@pytest.fixture(scope="session")
def milk_ing(food_kg, test_ingredient_vars):
    return food_kg.get_ingredient_by_uri(ing_uri=test_ingredient_vars.milk_uri)


@pytest.fixture(scope="session")
def butter_ing(food_kg, test_ingredient_vars):
    return food_kg.get_ingredient_by_uri(ing_uri=test_ingredient_vars.butter_uri)


from rdflib import URIRef


@pytest.fixture(scope="session")
def test_user(food_kg, test_user_vars, test_ingredient_vars):
    if FIVETHOUSAND_RECIPES_REMOTE:
        fav_recipes = {test_ingredient_vars.spin_cass_recipe_uri}
    else:
        fav_recipes = {test_ingredient_vars.lamb_gratin_recipe_uri}
    return FoodKgUser(
        uri=test_user_vars.user_uri,
        name="Testuser",
        sex="male",
        favorite_recipe_uri_set=frozenset(fav_recipes),
        prohibited_ingredient_uri_set=frozenset({ingredient_ns["milk"]}),
        prohibited_foodon_class_set=frozenset(
            {rdflib.URIRef("http://purl.obolibrary.org/obo/FOODON_00001256")}
        ),
        nutrition_constraint_set=frozenset({"reduce carbs"}),
        available_ingredient_uri_set=frozenset(
            {
                ing_uri
                for ing_uri in {
                    ingredient_ns["garlic%20clove"],
                    ingredient_ns["ground%20nutmeg"],
                    ingredient_ns["potato"],
                    ingredient_ns["heavy%20cream"],
                    ingredient_ns["parmesan%20cheese"],
                    ingredient_ns["salt%20and%20pepper"],
                    ingredient_ns["Worcestershire%20sauce"],
                    ingredient_ns["carrot"],
                    ingredient_ns["frozen%20peas"],
                    ingredient_ns["ground%20beef"],
                    ingredient_ns["onion"],
                    ingredient_ns["salt%20and%20pepper"],
                    ingredient_ns["tomato%20soup"],
                    ingredient_ns["unsalted%20butter"],
                    ingredient_ns["water"],
                }
            }
        ),
    )


@pytest.fixture(scope="session")
def test_user_2(food_kg, test_user_vars, test_ingredient_vars):
    return FoodKgUser(
        uri=test_user_vars.user_uri_2,
        name="Testuser 2",
        sex="male",
        age=40,
        bmi=30.0,
        favorite_recipe_uri_set=frozenset(
            {test_ingredient_vars.lamb_gratin_recipe_uri}
        ),
        prohibited_ingredient_uri_set=frozenset(),
        prohibited_foodon_class_set=frozenset(),
        nutrition_constraint_set=frozenset(),
        available_ingredient_uri_set=frozenset(),
    )


@pytest.fixture(scope="session")
def placeholder_guideline_comp(guideline_kg):
    return guideline_kg.temp_guideline_uri_dict[cfg.HARDCODED_GUIDELINE_URI_1]


@pytest.fixture(scope="session")
def placeholder_guideline2_comp(guideline_kg):
    return guideline_kg.temp_guideline_uri_dict[cfg.HARDCODED_GUIDELINE_URI_2]


@pytest.fixture(scope="session")
def placeholder_guideline():
    conditions = frozenset({})
    explanation = Explanation(
        explanation_string="As for the general population, people with diabetes should limit sodium consumption to <2,300 mg/day."
    )

    return Guideline(
        uri=cfg.HARDCODED_GUIDELINE_URI_1,
        user_conditions=conditions,
        filter_directives=frozenset(),
        scoring_directives=frozenset(
            {
                GuidelineDirective(
                    target_value=2300,
                    target_attribute="total_nutritional_info.sodium_mg",
                    directive_type=ConstraintType.LEQ,
                )
            }
        ),
        explanation=explanation,
    )


@pytest.fixture(scope="session")
def placeholder_guideline2():
    conditions = frozenset(
        {lambda usr: usr.sex == "male", lambda usr: usr.bmi is not None and usr.bmi > 0}
    )
    explanation = Explanation(
        explanation_string="1,500–1,800 kcal/day for men, adjusted for the individuals baseline body weight"
    )

    return Guideline(
        uri=cfg.HARDCODED_GUIDELINE_URI_2,
        user_conditions=conditions,
        filter_directives=frozenset(),
        scoring_directives=frozenset(
            {
                GuidelineDirective(
                    target_value=1800,
                    target_attribute="total_nutritional_info.energ__kcal",
                    directive_type=ConstraintType.LEQ,
                )
            }
        ),
        explanation=explanation,
    )


@pytest.fixture(scope="session")
def test_user_vars():
    class TestUserVars:
        user_uri = rdflib.URIRef("http://idea.rpi.edu/heals/kb/user/user_id/USER_001")
        user_uri_2 = rdflib.URIRef("http://idea.rpi.edu/heals/kb/user/user_id/USER_002")

    return TestUserVars


@pytest.fixture(scope="session")
def test_ingredient_vars():
    class TestIngVars:
        """
        pytest doesn't allow class fixtures
        """

        peanut_oil_uri = ingredient_ns["peanut%20oil"]
        peanut_butter_uri = ingredient_ns["peanut%20butter"]
        potato_uri = ingredient_ns["potato"]
        potato_usda = usda_equiv = rdflib.URIRef(
            "http://idea.rpi.edu/heals/kb/usda#11370"
        )
        dummy_potato_ing = FoodKgIngredient(
            uri=potato_uri,
            label="potatoes",
            usda_equiv=rdflib.URIRef("http://idea.rpi.edu/heals/kb/usda#11370"),
            nutrition_info=NutritionInfo(),
        )
        butter_uri = ingredient_ns["butter"]
        dummy_butter_ing = FoodKgIngredient(
            uri=butter_uri,
            label="butter",
            usda_equiv=rdflib.URIRef("http://idea.rpi.edu/heals/kb/usda#01001"),
            nutrition_info=NutritionInfo(),
        )
        butter_inguse_uri = rdflib.URIRef(
            "http://idea.rpi.edu/heals/kb/recipe/4849bd3f-Crunchy%2C%20Easy%2C%20Onion%20Garlic%20Potatoes/ingredient/butter"
        )
        milk_uri = ingredient_ns["milk"]
        dummy_milk_ing = FoodKgIngredient(
            uri=milk_uri,
            label="milk",
            usda_equiv=rdflib.URIRef("http://idea.rpi.edu/heals/kb/usda#01059"),
            nutrition_info=NutritionInfo(),
        )

        cauliflower_uri = ingredient_ns["cauliflower"]
        carrot_uri = ingredient_ns["carrot"]
        butter_uri = ingredient_ns["butter"]
        butternut_uri = ingredient_ns["butternut%20squash"]
        turnip_uri = ingredient_ns["turnip"]
        unsaltedbutter_uri = ingredient_ns["unsalted%20butter"]

        onion_garlic_pot_recipe_uri = recipe_ns[
            "4849bd3f-Crunchy%2C%20Easy%2C%20Onion%20Garlic%20Potatoes"
        ]
        layer_din_recipe_uri = recipe_ns["ea77d0d2-Layered%20Dinner"]
        amish_soup_recipe_uri = recipe_ns["00a5cb5c86-Amish%20Chicken%20Corn%20Soup"]
        lamb_gratin_recipe_uri = recipe_ns["001310c451-Lamb%20Chops%20au%20Gratin"]
        gratin_potato_recipe_uri = recipe_ns["d4440bcd-Gratin%20Potatoes"]
        spin_cass_recipe_uri = recipe_ns["00f4634369-Spinach%20Phyllo%20Casserole"]

        inguse_ns = rdflib.Namespace(
            "http://idea.rpi.edu/heals/kb/recipe/4849bd3f-Crunchy%2C%20Easy%2C%20Onion%20Garlic%20Potatoes/ingredient/"
        )
        onion_garlic_pot_ing_use_uris = {
            inguse_ns["French%20-%20fried%20onions"],
            inguse_ns["butter"],
            inguse_ns["dried%20garlic"],
            inguse_ns["milk"],
            inguse_ns["potatoes"],
        }

        ings_cooccurring_with_potatoes = {
            ingredient_ns["French%20-%20fried%20onions"],
            ingredient_ns["Worcestershire%20sauce"],
            ingredient_ns["butter"],
            ingredient_ns["carrot"],
            ingredient_ns["dried%20garlic"],
            ingredient_ns["frozen%20peas"],
            ingredient_ns["garlic%20clove"],
            ingredient_ns["ground%20beef"],
            ingredient_ns["ground%20nutmeg"],
            ingredient_ns["heavy%20cream"],
            ingredient_ns["milk"],
            ingredient_ns["onion"],
            ingredient_ns["parmesan%20cheese"],
            ingredient_ns["salt%20and%20pepper"],
            ingredient_ns["tomato%20soup"],
            ingredient_ns["water"],
        }

        potato_subs_uris = {carrot_uri, cauliflower_uri, turnip_uri, butternut_uri}
        low_carb_carrot_subs = {cauliflower_uri, turnip_uri}
        carrot_subs_uris = {cauliflower_uri, turnip_uri, butternut_uri, potato_uri}
        butter_subs_uris = {
            ingredient_ns["unsweetened%20applesauce"],
            ingredient_ns["olive%20oil"],
            ingredient_ns["prune%20puree"],
            ingredient_ns["unsalted%20butter"],
            ingredient_ns["shortening"],
        }

        dairy_food_product = rdflib.URIRef(
            "http://purl.obolibrary.org/obo/FOODON_00001256"
        )

    return TestIngVars
