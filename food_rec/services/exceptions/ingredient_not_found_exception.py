from food_rec.services.exceptions import NotFoundException
from rdflib import URIRef
from typing import Optional


class IngredientNotFoundException(NotFoundException):
    def __init__(self, *, ing_uri: URIRef, message: Optional[str] = None):
        if not message:
            message = f"Ingredient not found: {ing_uri}"
        NotFoundException.__init__(self, uri=ing_uri, message=message)
