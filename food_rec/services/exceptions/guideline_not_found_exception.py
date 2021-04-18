from food_rec.services.exceptions import NotFoundException
from rdflib import URIRef
from typing import Optional


class GuidelineNotFoundException(NotFoundException):
    def __init__(self, *, guideline_uri: URIRef, message: Optional[str] = None):
        if not message:
            message = f"Guideline not found: {guideline_uri}"
        NotFoundException.__init__(self, uri=guideline_uri, message=message)
