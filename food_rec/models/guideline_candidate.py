from frex.models import Candidate
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from food_rec.models import Guideline, PatientContext


@dataclass_json
@dataclass
class GuidelineCandidate(Candidate):
    """
    A candidate for guidelines that are generated to be matched to a patient.
    """

    context: PatientContext
    domain_object: Guideline
