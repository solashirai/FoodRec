from typing import Tuple
from food_rec.models import *
from food_rec.services import ExplainableFoodRecommenderService
from food_rec.services.food import RecipeEmbeddingService, FoodKgQueryService
from food_rec.services.user import UserKgQueryService
from food_rec.services.guideline import GuidelineKgQueryService
from food_rec.pipeline import (
    RecommendRecipesPipeline,
    RecommendMealPlanPipeline,
    ApplyGuidelinesToRecipesPipeline,
)
from frex.models import Explanation, ConstraintSolution
from frex.models.constraints import ConstraintSolutionSection
from frex.utils import ConstraintSolver


class GraphExplainableFoodRecommenderService(ExplainableFoodRecommenderService):
    """
    A query service to retrieve explainable recipe recommendations and meal plans for a user.
    Recommendations are retrieved using a recommender pipeline, which also should be applying
    the relevant explanations.
    """

    def __init__(
        self,
        *,
        food_kg: FoodKgQueryService,
        user_kg: UserKgQueryService,
        guideline_kg: GuidelineKgQueryService,
        recipe_embedding_service: RecipeEmbeddingService
    ):
        self.food_kg = food_kg
        self.user_kg = user_kg
        self.guideline_kg = guideline_kg
        self.recipe_embedding_service = recipe_embedding_service

    def get_recipe_recommendations_for_user(
        self, *, user: FoodKgUser, number_of_recipes: int
    ) -> Tuple[RecipeRecommendation]:
        """
        Use a recipe recommendation pipeline to retrieve recommended recipes for a taret user.

        :param user: The user context to retrieve recommendations for
        :param number_of_recipes: The number of recommended recipes to return
        :return: A tuple of RecipeRecommendation objects
        """

        rr_pipeline = RecommendRecipesPipeline(
            recipe_embedding_service=self.recipe_embedding_service,
            food_kg=self.food_kg,
            guideline_pipe=ApplyGuidelinesToRecipesPipeline(
                guideline_kg=self.guideline_kg
            ),
        )
        candidates = list(rr_pipeline(context=PatientContext(target_user=user)))

        candidates = candidates[:number_of_recipes]
        return tuple(
            RecipeRecommendation(
                recipe=candidate.domain_object,
                explanation=RecipeRecommendationExplanation(
                    explanation_contents=tuple(candidate.applied_explanations)
                ),
            )
            for candidate in candidates
        )

    def get_meal_plan_for_user(
        self, *, user: FoodKgUser, number_of_days: int, meals_per_day: int = 3
    ) -> MealPlanCandidate:
        """
        Use a meal plan recommendation pipeline to retrieve a meal plan for a target user.
        Currently not properly developed, just uses recommended recipes and puts them into a meal plan object.

        :param user: the target user context
        :param number_of_days: the number of days to include in the meal plans
        :param meals_per_day: the number of meals that should be contained in each day of the meal plan
        :return: a MealPlan to recommend to the user.
        """

        mp_pipeline = RecommendMealPlanPipeline(
            recipe_embedding_service=self.recipe_embedding_service,
            food_kg=self.food_kg,
            guideline_kg=self.guideline_kg,
            number_of_days=number_of_days,
            meals_per_day=meals_per_day,
        )

        soln = list(mp_pipeline(context=PatientContext(target_user=user)))[0]

        return soln
