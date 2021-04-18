from food_rec.services.exceptions import MalformedContentException
from rdflib import URIRef
from typing import Optional


class MalformedUserException(MalformedContentException):
    def __init__(self, *, user_uri: URIRef, message: Optional[str] = None):
        if not message:
            message = f"User content malformed: {user_uri}"
        MalformedContentException.__init__(self, uri=user_uri, message=message)
