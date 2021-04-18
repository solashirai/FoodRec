from food_rec.services.exceptions import CustomException
from rdflib import URIRef
from typing import Optional


class MalformedContentException(CustomException):
    def __init__(self, *, uri: URIRef, message: Optional[str] = None):
        self.__uri = uri
        if not message:
            message = f"Content malformed: {uri}"
        CustomException.__init__(self, message=message)

    @property
    def uri(self) -> URIRef:
        return self.__uri
