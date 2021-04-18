from food_rec.services.exceptions import NotFoundException
from rdflib import URIRef
from typing import Optional


class UsdaFoodNotFoundException(NotFoundException):
    def __init__(self, *, usda_food_uri: URIRef, message: Optional[str] = None):
        if not message:
            message = f"Usda food not found: {usda_food_uri}"
        NotFoundException.__init__(self, uri=usda_food_uri, message=message)
