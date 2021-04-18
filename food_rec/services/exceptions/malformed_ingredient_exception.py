from food_rec.services.exceptions import MalformedContentException
from rdflib import URIRef
from typing import Optional


class MalformedIngredientException(MalformedContentException):
    def __init__(self, *, ing_uri: URIRef, message: Optional[str] = None):
        if not message:
            message = f"Ingredient content malformed: {ing_uri}"
        MalformedContentException.__init__(self, uri=ing_uri, message=message)
