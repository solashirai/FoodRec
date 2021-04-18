from food_rec.services.exceptions import NotFoundException
from rdflib import URIRef
from typing import Optional


class UserNotFoundException(NotFoundException):
    def __init__(self, *, user_uri: URIRef, message: Optional[str] = None):
        if not message:
            message = f"User not found: {user_uri}"
        NotFoundException.__init__(self, uri=user_uri, message=message)
