from typing import Dict
from rdflib.term import URIRef
from typing import Optional, NamedTuple
from food_rec.models import NutritionInfo
from frex import DomainObject
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True)
class FoodKgIngredient(DomainObject):
    """
    Class to store information about a particular ingredient found in FoodKG.

    Includes the URI of the ingredient so that it can be used again in later queries.
    Currently also includes information about USDA nutrition, but unsure if this should be stored in the object
    or if it should just be retrieved via sparql when needed.
    """

    label: str
    # for documentation on nutrition info https://data.nal.usda.gov/system/files/sr27_doc.pdf
    # nutrients seem to be showing as amount present in 100g of the food product, so no normalization needed
    usda_equiv: Optional[URIRef]
    nutrition_info: NutritionInfo
