from frex.pipelines import Pipeline
from frex.models import Candidate, Explanation
from food_rec.models import *
from food_rec.services.guideline import GuidelineKgQueryService
from food_rec.pipeline_stages import *
from typing import Generator, Optional


class GenerateGuidelinesApplicableToUserPipeline(Pipeline):
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
                AllGuidelinesCandidateGenerator(
                    guideline_query_service=self.guideline_kg
                ),
                UserMatchGuidelineFilter(
                    filter_explanation=Explanation(
                        "User matches the conditions to apply this guideline."
                    )
                ),
            ),
        )
