from food_rec.services.exceptions import MalformedContentException
from rdflib import URIRef
from typing import Optional


class MalformedIngredientUseException(MalformedContentException):
    def __init__(self, *, ing_use_uri: URIRef, message: Optional[str] = None):
        if not message:
            message = f"Ingredient use content malformed: {ing_use_uri}"
        MalformedContentException.__init__(self, uri=ing_use_uri, message=message)
