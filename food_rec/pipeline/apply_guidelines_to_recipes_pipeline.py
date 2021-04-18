from frex.pipelines import Pipeline
from frex.models import Candidate, Explanation
from food_rec.models import *
from food_rec.services.guideline import GuidelineKgQueryService
from food_rec.pipeline_stages import *
from food_rec.pipeline import GenerateGuidelinesApplicableToUserPipeline
from typing import Generator, Optional


class ApplyGuidelinesToRecipesPipeline(Pipeline):
    """
    A pipeline to generate guidelines that should be applied to a target patient context.

    Currently the generator will return all guidelines as candidates, which will then be filtered down
    based on the patient's context.
    """

    def __init__(self, *, guideline_kg: GuidelineKgQueryService):
        self.guideline_kg = guideline_kg
        Pipeline.__init__(
            self,
            stages=(
                GenerateGuidelinesApplicableToUserPipeline(guideline_kg=guideline_kg),
            ),
        )

    def __call__(
        self,
        *,
        candidates: Optional[Generator[Candidate, None, None]] = None,
        context: Optional[object] = None,
    ) -> Generator[Candidate, None, None]:
        guideline_candidates = list(Pipeline.__call__(self, context=context))
        guideline_stages = [
            UserGuidelineApplicationPipelineStage(guideline=gc.domain_object)
            for gc in guideline_candidates
        ]

        for g_stage in guideline_stages:
            candidates = g_stage(context=context, candidates=candidates)
        return candidates
