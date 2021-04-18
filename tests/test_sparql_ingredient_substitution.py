from food_rec.services import GraphIngredientSubstitutionService
from food_rec.services.food import LocalGraphFoodKgQueryService
from food_rec.services.user import LocalGraphUserKgQueryService
from food_rec.models import *


def test_get_substitutions_for_ingredient_for_user(
    food_kg_subs: GraphIngredientSubstitutionService,
    food_kg: LocalGraphFoodKgQueryService,
    user_kg: LocalGraphUserKgQueryService,
    test_user_vars,
    test_ingredient_vars,
):
    carrot = food_kg.get_ingredient_by_uri(ing_uri=test_ingredient_vars.carrot_uri)
    user = user_kg.get_user_by_uri(user_uri=test_user_vars.user_uri)
    subs = food_kg_subs.get_substitutions_for_ingredient(ingredient=carrot, user=user)

    expected_subs = [
        FoodKgIngredientSubstitutionOption(
            from_ing=food_kg.get_ingredient_by_uri(
                ing_uri=test_ingredient_vars.carrot_uri
            ),
            explanation="fake explanation hardcoded sub",
            to_ing=food_kg.get_ingredient_by_uri(ing_uri=uri),
        )
        for uri in test_ingredient_vars.low_carb_carrot_subs
    ]

    assert set(expected_subs) == set(subs)


def test_get_substitutions_for_recipe_for_user(
    food_kg_subs: GraphIngredientSubstitutionService,
    food_kg: LocalGraphFoodKgQueryService,
    user_kg: LocalGraphUserKgQueryService,
    test_user_vars,
    test_ingredient_vars,
):
    recipe = food_kg.get_recipe_by_uri(
        recipe_uri=test_ingredient_vars.layer_din_recipe_uri
    )
    user = user_kg.get_user_by_uri(user_uri=test_user_vars.user_uri)
    subs = food_kg_subs.get_substitutions_for_recipe(recipe=recipe, user=user)

    expected_subs = [
        FoodKgIngredientSubstitutionOption(
            from_ing=food_kg.get_ingredient_by_uri(
                ing_uri=test_ingredient_vars.carrot_uri
            ),
            explanation="fake explanation hardcoded sub",
            to_ing=food_kg.get_ingredient_by_uri(ing_uri=uri),
        )
        for uri in test_ingredient_vars.low_carb_carrot_subs
    ]
    expected_subs.extend(
        [
            FoodKgIngredientSubstitutionOption(
                from_ing=food_kg.get_ingredient_by_uri(
                    ing_uri=test_ingredient_vars.potato_uri
                ),
                explanation="fake explanation hardcoded sub",
                to_ing=food_kg.get_ingredient_by_uri(ing_uri=uri),
            )
            for uri in test_ingredient_vars.potato_subs_uris
        ]
    )

    assert set(expected_subs) == set(subs)


def test_get_substitutions_for_recipe_for_user_2(
    food_kg_subs: GraphIngredientSubstitutionService,
    food_kg: LocalGraphFoodKgQueryService,
    user_kg: LocalGraphUserKgQueryService,
    test_ingredient_vars,
    test_user_vars,
):
    recipe = food_kg.get_recipe_by_uri(
        recipe_uri=test_ingredient_vars.layer_din_recipe_uri
    )
    user = user_kg.get_user_by_uri(user_uri=test_user_vars.user_uri_2)
    subs = food_kg_subs.get_substitutions_for_recipe(recipe=recipe, user=user)

    expected_subs = [
        FoodKgIngredientSubstitutionOption(
            from_ing=food_kg.get_ingredient_by_uri(
                ing_uri=test_ingredient_vars.carrot_uri
            ),
            explanation="fake explanation hardcoded sub",
            to_ing=food_kg.get_ingredient_by_uri(ing_uri=uri),
        )
        for uri in test_ingredient_vars.carrot_subs_uris
    ]
    expected_subs.extend(
        [
            FoodKgIngredientSubstitutionOption(
                from_ing=food_kg.get_ingredient_by_uri(
                    ing_uri=test_ingredient_vars.potato_uri
                ),
                explanation="fake explanation hardcoded sub",
                to_ing=food_kg.get_ingredient_by_uri(ing_uri=uri),
            )
            for uri in test_ingredient_vars.potato_subs_uris
        ]
    )

    assert set(expected_subs) == set(subs)
