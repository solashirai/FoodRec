from food_rec.models import FoodKgIngredient, NutritionInfo
from frex import DomainObject
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True)
class FoodKgIngredientUse(DomainObject):
    """
    Class to store information about an ingredient usage found in FoodKG.
    This differs from FoodKGIngredient because it is specific to a recipe and thus has a corresponding quantity.
    """

    foodkg_quantity: float
    quantity_units: str
    gram_quantity: float
    ingredient: FoodKgIngredient
    total_nutrition_info: NutritionInfo
