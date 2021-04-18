from food_rec.models import RecipeRecommendation
from typing import Tuple, NamedTuple
from frex import Explanation


class MealPlanDay(NamedTuple):
    """
    Class to store information about a day in a meal plan, composed of a number of recipe recommendations.

    Currently not fully developed.
    """

    recipe_recommendations: Tuple[RecipeRecommendation, ...]
    explanation: Explanation
