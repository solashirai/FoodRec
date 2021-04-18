from frex.pipeline_stages import PipelineStage
from frex.models import Candidate, Explanation
from food_rec.models import Guideline, PatientContext
from food_rec.pipeline_stages import GuidelineDirectiveScorer, GuidelineDirectiveFilter
from typing import Tuple, Generator, Any


class UserGuidelineApplicationPipelineStage(PipelineStage):
    """
    A pipeline stage that applies guideline directives if the current user context matches
    the guideline's conditions. Directives are represented as pipeline stages, so if the user
    matches with a guideline the candidate recipes may be filtered or scored based on the guideline.

    If the user does not meet the guideline conditions, candidates are passed through without changes.
    """

    def __init__(self, *, guideline: Guideline, **kwargs):
        self.guideline = guideline
        stages = []
        for filter_fun in guideline.filter_directives:
            stages.append(
                GuidelineDirectiveFilter(
                    directive_fun=filter_fun, filter_explanation=guideline.explanation
                )
            )
        for score_fun in guideline.scoring_directives:
            stages.append(
                GuidelineDirectiveScorer(
                    directive_fun=score_fun,
                    success_scoring_explanation=Explanation(
                        explanation_string=f"Adheres to guideline: {guideline.explanation.explanation_string}"
                    ),
                    failure_scoring_explanation=Explanation(
                        explanation_string=f"Does not adhere to guideline: {guideline.explanation.explanation_string}"
                    ),
                )
            )
        self.stages = tuple(stages)
        PipelineStage.__init__(self, **kwargs)

    def __call__(
        self, *, candidates: Generator[Candidate, None, None], context: PatientContext
    ) -> Generator[Candidate, None, None]:
        if all(
            condition(context.target_user)
            for condition in self.guideline.user_conditions
        ):
            for stage in self.stages:
                candidates = stage(candidates=candidates, context=context)
        yield from candidates
