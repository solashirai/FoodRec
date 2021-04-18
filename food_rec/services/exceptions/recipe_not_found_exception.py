from food_rec.services.exceptions import NotFoundException
from rdflib import URIRef
from typing import Optional


class RecipeNotFoundException(NotFoundException):
    def __init__(self, *, recipe_uri: URIRef, message: Optional[str] = None):
        if not message:
            message = f"Recipe not found: {recipe_uri}"
        NotFoundException.__init__(self, uri=recipe_uri, message=message)
