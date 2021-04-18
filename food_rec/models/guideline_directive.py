from typing import FrozenSet, TypeVar, List, Set, Callable, NamedTuple
from food_rec.models import FoodKgRecipe, FoodKgUser, RecipeCandidate
from frex import DomainObject, Explanation
from frex.models.constraints import ConstraintType
from frex.utils.common import rgetattr


class GuidelineDirective(NamedTuple):
    """
    Class to store information about a guideline directive, which takes the form of a type of constraint
    (EQ, LEQ, etc) used to compare a recipe's target attribute against some value.

    This may be expanded later to check more aspects of recipes, e.g., if some ingredient is in a recipe, but it's
    not too flexible right now.
    """

    target_value: float
    target_attribute: str
    directive_type: ConstraintType

    def __call__(self, *, candidate: RecipeCandidate):
        return self.directive_type(
            rgetattr(candidate.domain_object, self.target_attribute), self.target_value
        )
