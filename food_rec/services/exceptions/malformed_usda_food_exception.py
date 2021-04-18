from food_rec.services.exceptions import MalformedContentException
from rdflib import URIRef
from typing import Optional


class MalformedUsdaFoodException(MalformedContentException):
    def __init__(self, *, usda_food_uri: URIRef, message: Optional[str] = None):
        if not message:
            message = f"Usda food content malformed: {usda_food_uri}"
        MalformedContentException.__init__(self, uri=usda_food_uri, message=message)
