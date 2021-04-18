from food_rec.models import MealPlanDay
from typing import Tuple, NamedTuple
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from frex import Explanation


@dataclass_json
class MealPlanRecommendation(NamedTuple):
    """
    Class to store information about a meal plan, composed of a number of meal plan days which each contain recipes
    to eat.

    Currently not fully developed.
    """

    meal_plan_days: Tuple[MealPlanDay, ...]
    explanation: Explanation
