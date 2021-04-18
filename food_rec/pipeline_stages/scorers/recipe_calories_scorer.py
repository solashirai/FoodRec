from frex import CandidateScorer
from typing import Tuple
from food_rec.models import PatientContext, RecipeCandidate


class RecipeCaloriesScorer(CandidateScorer):
    """
    Score a recipe based on its calorie content.

    This is a dummy scorer that is only really applicable to help break ties in the current system,
    and it does not reflect any real guideline.
    """

    def score(self, *, candidate: RecipeCandidate) -> float:
        return 1 - candidate.domain_object.total_nutritional_info.energ__kcal / 1000.0
