from dataclasses_json import dataclass_json
from dataclasses import dataclass
from food_rec.models import FoodKgUser


@dataclass_json
@dataclass
class PatientContext:
    """
    Context wrapper for a FoodKgUser. Currently only stores information about the target user.
    """

    target_user: FoodKgUser
