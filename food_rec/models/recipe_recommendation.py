from food_rec.models import FoodKgRecipe, Guideline
from typing import Tuple, NamedTuple
from frex import Explanation


class RecipeRecommendation(NamedTuple):
    """
    Class to store information about a recipe recommendation.
    """

    recipe: FoodKgRecipe
    explanation: Explanation
