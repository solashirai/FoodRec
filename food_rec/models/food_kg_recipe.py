from typing import Set, Dict, FrozenSet, NamedTuple
from rdflib.term import URIRef
from food_rec.models import (
    FoodKgIngredientUse,
    FoodKgIngredient,
    NutritionInfo,
)
from collections import defaultdict
from frex import DomainObject
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True)
class FoodKgRecipe(DomainObject):
    """
    Class to store information about recipes found in FoodKG.
    Includes the URI of the recipe. Ingredients can be added/removed, and nutrition information about the overall
    recipe is computed based on the ingredients currently included in its ingredient list.
    """

    name: str
    id: str
    ingredient_use_set: FrozenSet[FoodKgIngredientUse]
    ingredient_set: FrozenSet[FoodKgIngredient]
    total_nutritional_info: NutritionInfo

    @staticmethod
    def get_total_nutrition_info(ing_uses: Set[FoodKgIngredientUse]) -> NutritionInfo:
        """
        Calculate the total nutritional information about each of the ingredients contained in the recipe.

        :return: A dictionary containing the total nutrition values summed up from the individual ingredients.
        """
        nutrition_dict = defaultdict(lambda: 0)
        for ing_use in ing_uses:
            for key in ing_use.total_nutrition_info._fields:
                if key not in {"gm_wt_1", "gm_wt_2"}:
                    val = getattr(ing_use.total_nutrition_info, key)

                    if isinstance(val, float):
                        nutrition_dict[key] += val

        # rounding should be happening in ingredient uses, but floats still seem to often not be properly rounded?
        # so round them again to be sure we don't get issues with weird rounding...
        for k in nutrition_dict.keys():
            nutrition_dict[k] = round(nutrition_dict[k], 6)
        return NutritionInfo(**nutrition_dict)
