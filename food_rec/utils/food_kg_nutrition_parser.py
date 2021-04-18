from food_rec.models import NutritionInfo


class FoodKgNutritionParser:
    @staticmethod
    def compute_total_nutrition_info(
        nutrition_info: NutritionInfo, gram_quantity: float
    ) -> NutritionInfo:
        """
        Compute the total nutritional values for this ingredient, taking gram_quantity into consideration.
        nutrition_info is expected to contain nutrient info per 100g of the ingredient.

        :return: a modified dictionary of nutrition info, multiplied by the appropriate amount of ingredient
        """
        total_nutrition = dict()
        for key in nutrition_info._fields:
            val = getattr(nutrition_info, key)
            if isinstance(val, float) or isinstance(val, int):
                total_nutrition[key] = round(gram_quantity * (val / 100.0), 6)
            else:
                total_nutrition[key] = val
        return NutritionInfo(**total_nutrition)
