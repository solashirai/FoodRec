from frex import CandidateBoolScorer
from typing import Tuple
from food_rec.models import PatientContext, RecipeCandidate


class SodiumBelowTargetScorer(CandidateBoolScorer):
    """
    Score a candidate recipe based on whether it has fewer than the target amount of sodium.

    Currently hard-coded to 2300 mg.
    """

    def score(self, *, candidate: RecipeCandidate) -> Tuple[bool, float]:
        if candidate.domain_object.total_nutritional_info.sodium_mg < 2300:
            return True, 1
        else:
            return False, 0
