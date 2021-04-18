from frex import CandidateBoolScorer
from typing import Tuple
from food_rec.models import PatientContext, RecipeCandidate


class CaloriesBelowTargetScorer(CandidateBoolScorer):
    """
    Score a candidate recipe based on whether it has fewer than the target number of calories.

    Currently hard-coded to 1800.
    """

    context: PatientContext

    def score(self, *, candidate: RecipeCandidate) -> Tuple[bool, float]:
        if candidate.domain_object.total_nutritional_info.energ__kcal < 1800:
            return True, 1
        else:
            return False, 0
