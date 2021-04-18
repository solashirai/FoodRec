from typing import List, Optional
from food_rec.models import *
from food_rec.services import IngredientSubstitutionService
from food_rec.services.food import FoodKgQueryService
from food_rec.services.user import UserKgQueryService


class GraphIngredientSubstitutionService(IngredientSubstitutionService):
    """
    A service to identify substitutions for ingredients.
    Currently only uses simple substitutions, i.e. relations present in the graph indicating that
    an ingredient is a substitute of another.
    """

    # prev_result_cache should be ResultCache instead of Graph?
    def __init__(self, *, food_kg: FoodKgQueryService, user_kg: UserKgQueryService):
        self.food_kg = food_kg
        self.user_kg = user_kg

    def get_substitutions_for_ingredient(
        self, *, ingredient: FoodKgIngredient, user: Optional[FoodKgUser]
    ) -> List[FoodKgIngredientSubstitutionOption]:
        """
        Retrieve simple substitutions from the FoodKG for a given input ingredient.
        Substitutions are then filtered out based on the user's prohibited ingredient information.

        :param ingredient: The ingredient to retrieve substitutions for
        :param user: the user context to filter substitutes
        :return: A list of ingredient substitution options fitting the input ingredient and user context
        """

        ing_uri = ingredient.uri
        sub_options = self.food_kg.get_simple_substitutions_by_ingredient_uri(
            ing_uri=ing_uri
        )
        if user:
            sub_options = self.filter_subs_for_user(user=user, substitutes=sub_options)
        return sub_options

    def get_substitutions_for_recipe(
        self, *, recipe: FoodKgRecipe, user: Optional[FoodKgUser]
    ) -> List[FoodKgIngredientSubstitutionOption]:
        """
        Retrieve substitutions from the FoodKG for a given input recipe.
        Substitutions are then filtered out based on the user's prohibited ingredient information.

        :param recipe: The recipe, containing ingredients whose substitutes will be searched for
        :param user: the user context to filter substitutes
        :return: A list of ingredient substitution options for ingredients in the recipe that fit the user context
        """
        recipe_uri = recipe.uri
        sub_options = self.food_kg.get_simple_substitutions_by_recipe_uri(
            recipe_uri=recipe_uri
        )
        if user:
            sub_options = self.filter_subs_for_user(user=user, substitutes=sub_options)
        return sub_options

    def filter_subs_for_user(
        self, *, user: FoodKgUser, substitutes: List[FoodKgIngredientSubstitutionOption]
    ) -> List[FoodKgIngredientSubstitutionOption]:
        """
        Filter out substitute options based on the user context of prohbited ingredients.

        :param user: the user context, containing prohibited ingredients and constraints
        :param substitutes: a list of substitutes to filter out
        :return: a modified list of substitution options who conform to the user's constraints
        """

        # currently only implementing a single simplified dietary constraint to tailor substitution to users
        user_constraints = user.nutrition_constraint_set
        bad_subs = set()
        if "reduce carbs" in user_constraints:
            for sub in substitutes:
                if (
                    sub.to_ing.nutrition_info.carbohydrt_g
                    > sub.from_ing.nutrition_info.carbohydrt_g
                ):
                    bad_subs.add(sub)
        return list(set(substitutes) - bad_subs)
