from frex import CandidateBoolScorer
from food_rec.models import PatientContext, RecipeCandidate, GuidelineDirective
from typing import Callable, Any, Tuple


class GuidelineDirectiveScorer(CandidateBoolScorer):
    """
    Score recipes based on some directive encoded in a guideline.
    """

    def __init__(self, *, directive_fun: GuidelineDirective, **kwargs):
        self.score_fun: GuidelineDirective = directive_fun
        CandidateBoolScorer.__init__(self, **kwargs)

    def score(self, *, candidate: RecipeCandidate) -> Tuple[bool, float]:
        if self.score_fun(candidate=candidate):
            return True, 1
        else:
            return False, 0
