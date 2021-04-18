from frex import CandidateGenerator, Explanation, Candidate
from typing import Generator, Dict, Tuple
from food_rec.models import FoodKgRecipe
from food_rec.services.guideline import GuidelineKgQueryService
from food_rec.services.food import RecipeEmbeddingService
from food_rec.models import PatientContext, GuidelineCandidate


class AllGuidelinesCandidateGenerator(CandidateGenerator):
    """
    Generate all current guidelines as candidates.
    """

    def __init__(self, *, guideline_query_service: GuidelineKgQueryService, **kwargs):
        self.gqs = guideline_query_service
        generator_explanation = Explanation(
            explanation_string="This is a guideline that exists in the system."
        )
        CandidateGenerator.__init__(
            self, generator_explanation=generator_explanation, **kwargs
        )

    def generate(
        self,
        *,
        candidates: Generator[Candidate, None, None] = None,
        context: PatientContext
    ) -> Generator[GuidelineCandidate, None, None]:
        if candidates:
            yield from candidates
        # currently just grabbing all guidelines for this generator
        all_guidelines = self.gqs.get_all_guidelines()
        for guideline in all_guidelines:
            yield GuidelineCandidate(
                context=context,
                domain_object=guideline,
                applied_explanations=[self.generator_explanation],
                applied_scores=[0],
            )
