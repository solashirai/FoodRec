from food_rec.services.exceptions import MalformedContentException
from rdflib import URIRef
from typing import Optional


class MalformedRecipeException(MalformedContentException):
    def __init__(self, *, recipe_uri: URIRef, message: Optional[str] = None):
        if not message:
            message = f"Recipe content malformed: {recipe_uri}"
        MalformedContentException.__init__(self, uri=recipe_uri, message=message)
