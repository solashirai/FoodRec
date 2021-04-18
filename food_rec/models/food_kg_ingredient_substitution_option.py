from typing import Dict, NamedTuple
from rdflib.term import URIRef, BNode
from food_rec.models import FoodKgIngredient


class FoodKgIngredientSubstitutionOption(NamedTuple):
    """
    Class to store information about a substitution option.

    In the substitution, from_ing is the ingredient to remove and to_ing is the ingredient
    to add in to the recipe.
    """

    from_ing: FoodKgIngredient
    explanation: str
    to_ing: FoodKgIngredient
