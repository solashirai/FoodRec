from frex.pipelines import Pipeline
from frex.pipeline_stages import CandidateRanker
from frex.models import Explanation, Candidate
from food_rec.services.food import RecipeEmbeddingService
from food_rec.services.food import FoodKgQueryService
from food_rec.services.guideline import GuidelineKgQueryService
from food_rec.pipeline_stages import *
from food_rec.pipeline import ApplyGuidelinesToRecipesPipeline
from food_rec.models import Guideline
from typing import Generator, Optional


class RecommendRecipesPipeline(Pipeline):
    """
    A pipeline to recommend recipes for a patient context.

    Candidates are generated based on similarity to the patient's favorite recipes.
    Scoring and filtering is based on guidelines, which are currently hardcoded in, and factors
    like prohibited ingredients for users.
    """

    def __init__(
        self,
        *,
        recipe_embedding_service: RecipeEmbeddingService,
        food_kg: FoodKgQueryService,
        guideline_kg: GuidelineKgQueryService
    ):
        self.res = recipe_embedding_service
        self.food_kg = food_kg

        Pipeline.__init__(
            self,
            stages=(
                SimilarToFavoritesRecipeCandidateGenerator(
                    recipe_embedding_service=self.res,
                    food_kg_query_service=self.food_kg,
                ),
                ContainsAnyProhibitedIngredientFilter(
                    filter_explanation=Explanation(
                        explanation_string="This recipe does not contain any ingredients that are prohibited by you."
                    )
                ),
                ApplyGuidelinesToRecipesPipeline(guideline_kg=guideline_kg),
                RecipeCaloriesScorer(
                    scoring_explanation=Explanation(
                        explanation_string="Scoring based on calories, this is mostly a placeholder to break ties."
                    )
                ),
                CandidateRanker(),
            ),
        )
