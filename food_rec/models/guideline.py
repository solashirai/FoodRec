from typing import FrozenSet, TypeVar, List, Set, Callable
from food_rec.models import FoodKgRecipe, FoodKgUser, GuidelineDirective
from frex import DomainObject, Explanation
from dataclasses import dataclass
from dataclasses_json import dataclass_json

T = TypeVar("T", int, float, str, List, Set, FrozenSet, FoodKgUser, FoodKgRecipe)


@dataclass_json
@dataclass(frozen=True)
class Guideline(DomainObject):
    """
    Class to store information about a healthy eating guideline.

    Current plan is to have this class contain the guideline condition, guideline directive,
    and textual explanation of the guideline.
    """

    # user_conditions and recipe_directives should be revisited in the future.
    # user_conditions currently are taking lambdas as input
    # recipe_directives maybe should eventually just be directly calling pipeline_stages to filter/score
    user_conditions: FrozenSet[Callable[[T], bool]]
    filter_directives: FrozenSet[GuidelineDirective]
    scoring_directives: FrozenSet[GuidelineDirective]
    explanation: Explanation
