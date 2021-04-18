from food_rec.services.exceptions import MalformedContentException
from rdflib import URIRef
from typing import Optional


class MalformedGuidelineException(MalformedContentException):
    def __init__(self, *, guideline_uri: URIRef, message: Optional[str] = None):
        if not message:
            message = f"Guideline content malformed: {guideline_uri}"
        MalformedContentException.__init__(self, uri=guideline_uri, message=message)
