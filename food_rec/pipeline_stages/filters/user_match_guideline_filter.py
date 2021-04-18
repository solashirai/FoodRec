from frex import CandidateFilterer
from food_rec.models import PatientContext, GuidelineCandidate


class UserMatchGuidelineFilter(CandidateFilterer):
    """
    Filter out guidelines that the patient's profile does not match with.

    All of the guideline's user_conditions must match with the patient context to pass
    through the filter.
    """

    context: PatientContext

    def filter(self, *, candidate: GuidelineCandidate) -> bool:
        return not all(
            condition(candidate.context.target_user)
            for condition in candidate.domain_object.user_conditions
        )
