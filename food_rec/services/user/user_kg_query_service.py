from abc import ABC, abstractmethod
from rdflib import URIRef
from food_rec.models import *


class UserKgQueryService(ABC):
    @abstractmethod
    def get_user_by_uri(self, *, user_uri: URIRef) -> FoodKgUser:
        pass
