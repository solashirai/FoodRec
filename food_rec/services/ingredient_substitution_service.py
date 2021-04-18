from abc import ABC, abstractmethod
from typing import List, Optional
from food_rec.models import *


class IngredientSubstitutionService(ABC):
    @abstractmethod
    def get_substitutions_for_ingredient(
        self, *, ingredient: FoodKgIngredient, user: Optional[FoodKgUser]
    ) -> List[FoodKgIngredientSubstitutionOption]:
        pass

    @abstractmethod
    def get_substitutions_for_recipe(
        self, *, recipe: FoodKgRecipe, user: Optional[FoodKgUser]
    ) -> List[FoodKgIngredientSubstitutionOption]:
        pass

    @abstractmethod
    def filter_subs_for_user(
        self, *, user: FoodKgUser, substitutes: List[FoodKgIngredientSubstitutionOption]
    ) -> List[FoodKgIngredientSubstitutionOption]:
        pass
