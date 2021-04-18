from frex import CandidateFilterer
from food_rec.models import PatientContext, RecipeCandidate


class ContainsAnyProhibitedIngredientFilter(CandidateFilterer):
    """
    Filter out recipes that contain an ingredient that is prohibited by the patient.
    """

    context: PatientContext

    def filter(self, *, candidate: RecipeCandidate) -> bool:
        return any(
            ing.uri in candidate.context.target_user.prohibited_ingredient_uri_set
            for ing in candidate.domain_object.ingredient_set
        )
