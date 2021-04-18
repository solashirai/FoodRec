from food_rec.services.exceptions import NotFoundException
from rdflib import URIRef
from typing import Optional


class IngredientUseNotFoundException(NotFoundException):
    def __init__(self, *, ing_use_uri: URIRef, message: Optional[str] = None):
        if not message:
            message = f"Ingredient use not found: {ing_use_uri}"
        NotFoundException.__init__(self, uri=ing_use_uri, message=message)
