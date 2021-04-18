from frex.pipelines import Pipeline
from frex.models import Explanation
from food_rec.models import *
from food_rec.services.food import RecipeEmbeddingService
from food_rec.services.food import FoodKgQueryService
from food_rec.services.guideline import GuidelineKgQueryService
from food_rec.pipeline_stages import *
from food_rec.pipeline import (
    RecommendRecipesPipeline,
    ApplyGuidelinesToRecipesPipeline,
)


class RecommendMealPlanPipeline(Pipeline):
    """
    A pipeline to recommend a meal plan for a patient context.

    Recipes to be included in the meal plan are generated using the RecommendRecipesPipeline.
    This is currently a very baseline implementation.
    """

    def __init__(
        self,
        *,
        recipe_embedding_service: RecipeEmbeddingService,
        food_kg: FoodKgQueryService,
        guideline_kg: GuidelineKgQueryService,
        number_of_days: int = 7,
        meals_per_day: int = 3
    ):
        self.res = recipe_embedding_service
        self.food_kg = food_kg

        Pipeline.__init__(
            self,
            stages=(
                RecommendRecipesPipeline(
                    recipe_embedding_service=recipe_embedding_service,
                    food_kg=food_kg,
                    guideline_kg=guideline_kg,
                ),
                MealPlanCandidateGenerator(
                    number_of_days=number_of_days, meals_per_day=meals_per_day
                ),
            ),
        )
