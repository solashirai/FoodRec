from typing import FrozenSet, Optional, NamedTuple
from rdflib import URIRef
from frex import DomainObject
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True)
class FoodKgUser(DomainObject):
    """
    To be implemented. Class to capture information about a User, to use for recommendations.

    Things User should eventually include:

    -Dietary restrictions
    --limitations of intake for certain nutrients
    --allergies

    -Food preferences
    --ingredients the user likes
    --ingredients the user dislikes

    -Eating history (maybe)
    --history of what recipes the user has made before (and indication of whether they liked/disliked it)
    --favorite recipes?
    --what has been eaten so far on a daily/weekly basis
    """

    name: str
    sex: str
    favorite_recipe_uri_set: FrozenSet[URIRef]
    prohibited_ingredient_uri_set: FrozenSet[URIRef]
    prohibited_foodon_class_set: FrozenSet[URIRef]
    available_ingredient_uri_set: FrozenSet[URIRef]
    age: Optional[int] = None
    bmi: Optional[float] = None
    target_lifestyle_guideline_set: Optional[FrozenSet[URIRef]] = frozenset()
    nutrition_constraint_set: Optional[FrozenSet[str]] = frozenset()
