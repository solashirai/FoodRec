from abc import ABC, abstractmethod
from typing import Tuple
from food_rec.models import *


class ExplainableFoodRecommenderService(ABC):
    @abstractmethod
    def get_recipe_recommendations_for_user(
        self, *, user: FoodKgUser, number_of_recipes: int
    ) -> Tuple[RecipeRecommendation]:
        pass

    @abstractmethod
    def get_meal_plan_for_user(
        self, *, user: FoodKgUser, number_of_meals: int
    ) -> MealPlanDay:
        pass
