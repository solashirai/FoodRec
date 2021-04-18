from frex import CandidateFilterer
from food_rec.models import PatientContext, RecipeCandidate, GuidelineDirective
from typing import Callable, Any


class GuidelineDirectiveFilter(CandidateFilterer):
    """
    Filter out recipes based on some directive encoded in a guideline.
    """

    def __init__(self, *, directive_fun: GuidelineDirective, **kwargs):
        self.filter_fun: GuidelineDirective = directive_fun
        CandidateFilterer.__init__(self, **kwargs)

    def filter(self, *, candidate: RecipeCandidate) -> bool:
        return self.filter_fun(candidate=candidate)
