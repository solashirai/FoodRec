from food_rec.models import *
from food_rec.services.food import LocalGraphFoodKgQueryService
from rdflib import URIRef
from food_rec.services.exceptions import *
import pytest


def test_raise_exceptions(food_kg: LocalGraphFoodKgQueryService):
    # testing that functions don't break down if they retrieve invalid recipe/ingredient/etc URIs
    with pytest.raises(RecipeNotFoundException):
        recipe = food_kg.get_recipe_by_uri(recipe_uri=URIRef("bad_recipe"))
    with pytest.raises(IngredientNotFoundException):
        ingredient = food_kg.get_ingredient_by_uri(ing_uri=URIRef("bad_ing"))
    with pytest.raises(IngredientUseNotFoundException):
        ing_use = food_kg.get_ingredient_use_by_uri(ing_use_uri=URIRef("bad_ing_use"))

    with pytest.raises(UsdaFoodNotFoundException):
        nutrition = food_kg.get_usda_nutrition_by_uri(usda_food_uri=URIRef("bad_usda"))

    with pytest.raises(IngredientNotFoundException):
        subs = food_kg.get_simple_substitutions_by_ingredient_uri(
            ing_uri=URIRef("bad_ing")
        )
    with pytest.raises(RecipeNotFoundException):
        recipe_subs = food_kg.get_simple_substitutions_by_recipe_uri(
            recipe_uri=URIRef("bad_recipe")
        )


def test_get_recipe_by_uri(food_kg: LocalGraphFoodKgQueryService, test_ingredient_vars):
    recipe = food_kg.get_recipe_by_uri(
        recipe_uri=test_ingredient_vars.onion_garlic_pot_recipe_uri
    )

    assert test_ingredient_vars.onion_garlic_pot_recipe_uri == recipe.uri


def test_get_recipes_by_uri(
    food_kg: LocalGraphFoodKgQueryService, test_ingredient_vars
):
    recipes = food_kg.get_recipes_by_uri(
        recipe_uris=(
            test_ingredient_vars.onion_garlic_pot_recipe_uri,
            test_ingredient_vars.gratin_potato_recipe_uri,
        )
    )
    expected_recipes = (
        food_kg.get_recipe_by_uri(
            recipe_uri=test_ingredient_vars.onion_garlic_pot_recipe_uri
        ),
        food_kg.get_recipe_by_uri(
            recipe_uri=test_ingredient_vars.gratin_potato_recipe_uri
        ),
    )
    assert expected_recipes == recipes


def test_get_ingredient_use_by_uri(
    food_kg: LocalGraphFoodKgQueryService, test_ingredient_vars
):
    ing_use = food_kg.get_ingredient_use_by_uri(
        ing_use_uri=test_ingredient_vars.butter_inguse_uri
    )

    expected_inguse = FoodKgIngredientUse(
        uri=test_ingredient_vars.butter_inguse_uri,
        foodkg_quantity=2.0,
        quantity_units="tablespoons",
        ingredient=food_kg.get_ingredient_by_uri(
            ing_uri=test_ingredient_vars.butter_uri
        ),
        gram_quantity=28.4,
        total_nutrition_info=NutritionInfo(
            shrt__desc="BUTTER,WITH SALT",
            gm_wt__desc1="1 pat,  (1 sq, 1/3 high)",
            gm_wt__desc2="1 tbsp",
            folate__tot_micro_g=0.852,
            vit__c_mg=0.0,
            vit__b6_mg=0.000852,
            food__folate_micro_g=0.852,
            thiamin_mg=0.00142,
            phosphorus_mg=6.816,
            cholestrl_mg=61.06,
            lipid__tot_g=23.03524,
            gm_wt_1=1.42,
            folate__d_f_e_micro_g=0.852,
            sodium_mg=182.612,
            alpha__carot_micro_g=0.0,
            ash_g=0.59924,
            retinol_micro_g=190.564,
            beta__crypt_micro_g=0.0,
            f_a__sat_g=14.588512,
            vit__a__r_a_e=194.256,
            carbohydrt_g=0.01704,
            vit__b12_micro_g=0.04828,
            gm_wt_2=4.0328,
            lut__zea__micro_g=0.0,
            choline__tot__mg=5.3392,
            protein_g=0.2414,
            water_g=4.50708,
            niacin_mg=0.011928,
            magnesium_mg=0.568,
            f_a__mono_g=5.969964,
            iron_mg=0.00568,
            beta__carot_micro_g=44.872,
            manganese_mg=0.0,
            vit__d__i_u=0.426,
            refuse__pct=0.0,
            vit__k_micro_g=1.988,
            fiber__t_d_g=0.0,
            potassium_mg=6.816,
            selenium_micro_g=0.284,
            lycopene_micro_g=0.0,
            copper_mg=0.0,
            riboflavin_mg=0.009656,
            calcium_mg=6.816,
            vit__d_micro_g=0.426,
            panto__acid_mg=0.03124,
            zinc_mg=0.02556,
            sugar__tot_g=0.01704,
            vit__e_mg=0.65888,
            energ__kcal=203.628,
            f_a__poly_g=0.864212,
            folic__acid_micro_g=0.0,
            vit__a__i_u=709.716,
        ),
    )

    assert (
        expected_inguse == ing_use
        and ing_use.total_nutrition_info == expected_inguse.total_nutrition_info
    )


def test_get_ingredient_by_uri(
    food_kg: LocalGraphFoodKgQueryService, potato_nutrition, test_ingredient_vars
):
    potato_ing = food_kg.get_ingredient_by_uri(ing_uri=test_ingredient_vars.potato_uri)
    expected_potato = FoodKgIngredient(
        uri=test_ingredient_vars.potato_uri,
        label="potatoes",
        usda_equiv=URIRef("http://idea.rpi.edu/heals/kb/usda#11370"),
        nutrition_info=potato_nutrition,
    )

    assert expected_potato.nutrition_info == potato_ing.nutrition_info


def test_get_usda_nutrition_by_uri(
    food_kg: LocalGraphFoodKgQueryService, potato_nutrition, test_ingredient_vars
):
    nutrition_dict = food_kg.get_usda_nutrition_by_uri(
        usda_food_uri=test_ingredient_vars.potato_usda
    )

    assert potato_nutrition == nutrition_dict


def test_get_simple_substitutions_by_ingredient_uri(
    food_kg: LocalGraphFoodKgQueryService, test_ingredient_vars
):
    subs = food_kg.get_simple_substitutions_by_ingredient_uri(
        ing_uri=test_ingredient_vars.potato_uri
    )

    expected_subs = [
        FoodKgIngredientSubstitutionOption(
            from_ing=food_kg.get_ingredient_by_uri(
                ing_uri=test_ingredient_vars.potato_uri
            ),
            explanation="fake explanation hardcoded sub",
            to_ing=food_kg.get_ingredient_by_uri(ing_uri=uri),
        )
        for uri in test_ingredient_vars.potato_subs_uris
    ]

    assert set(expected_subs) == set(subs)


def test_get_simple_substitutions_by_recipe_uri(
    food_kg: LocalGraphFoodKgQueryService, test_ingredient_vars
):
    subs = food_kg.get_simple_substitutions_by_recipe_uri(
        recipe_uri=test_ingredient_vars.onion_garlic_pot_recipe_uri
    )

    expected_subs = [
        FoodKgIngredientSubstitutionOption(
            from_ing=food_kg.get_ingredient_by_uri(
                ing_uri=test_ingredient_vars.potato_uri
            ),
            explanation="fake explanation hardcoded sub",
            to_ing=food_kg.get_ingredient_by_uri(ing_uri=uri),
        )
        for uri in test_ingredient_vars.potato_subs_uris
    ]
    expected_subs.extend(
        [
            FoodKgIngredientSubstitutionOption(
                from_ing=food_kg.get_ingredient_by_uri(
                    ing_uri=test_ingredient_vars.butter_uri
                ),
                explanation="fake explanation hardcoded sub",
                to_ing=food_kg.get_ingredient_by_uri(ing_uri=uri),
            )
            for uri in test_ingredient_vars.butter_subs_uris
        ]
    )

    assert set(expected_subs) == set(subs)


def test_get_all_recipes_not_using_ingredients(
    food_kg: LocalGraphFoodKgQueryService, test_ingredient_vars
):
    no_potato_recipes = food_kg.get_all_recipes_not_using_ingredients(
        prohibited_ing_uris={test_ingredient_vars.potato_uri}
    )
    no_potato_no_butter_recipes = food_kg.get_all_recipes_not_using_ingredients(
        prohibited_ing_uris={
            test_ingredient_vars.potato_uri,
            test_ingredient_vars.butter_uri,
        }
    )

    expected_np = frozenset(
        {
            food_kg.get_recipe_by_uri(
                recipe_uri=test_ingredient_vars.amish_soup_recipe_uri
            ),
            food_kg.get_recipe_by_uri(
                recipe_uri=test_ingredient_vars.lamb_gratin_recipe_uri
            ),
        }
    )
    expected_npnb = ()

    assert (
        frozenset(set(no_potato_recipes)) == expected_np
        and no_potato_no_butter_recipes == expected_npnb
    )


def test_get_all_recipes_not_using_foodon_subclasses(
    food_kg: LocalGraphFoodKgQueryService, test_ingredient_vars
):
    no_dairy_recipes = food_kg.get_all_recipes_not_using_foodon_subclasses(
        prohibited_foodon_uris={test_ingredient_vars.dairy_food_product}
    )

    expected_ndr = (
        food_kg.get_recipe_by_uri(recipe_uri=test_ingredient_vars.layer_din_recipe_uri),
    )

    assert no_dairy_recipes == expected_ndr
