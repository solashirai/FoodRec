from frex.models import Candidate
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from food_rec.models import MealPlanRecommendation, PatientContext


@dataclass_json
@dataclass
class MealPlanCandidate(Candidate):
    """
    A candidate meal plan that will be recommended to the target user, who is contained in
    the PatientContext.
    """

    context: PatientContext
    domain_object: MealPlanRecommendation
