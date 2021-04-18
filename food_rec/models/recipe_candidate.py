from frex.models import Candidate
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from food_rec.models import FoodKgRecipe, PatientContext


@dataclass_json
@dataclass
class RecipeCandidate(Candidate):
    """
    A candidate for Recipes that will be recommended to the target user, who is contained in
    the PatientContext.
    """

    context: PatientContext
    domain_object: FoodKgRecipe
