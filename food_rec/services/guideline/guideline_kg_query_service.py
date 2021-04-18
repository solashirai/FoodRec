from abc import ABC, abstractmethod
from rdflib import Graph, URIRef
from typing import Dict, Tuple, Optional
from food_rec.models import *


class GuidelineKgQueryService(ABC):
    @abstractmethod
    def get_all_guidelines(self) -> Tuple[Guideline]:
        pass

    @abstractmethod
    def get_guideline_by_uri(self, *, recipe_uri: FoodKgUser) -> Guideline:
        pass

    @abstractmethod
    def get_guidelines_by_conditions(
        self, *, age: Optional[int], bmi: Optional[float], sex: Optional[str]
    ) -> Tuple[Guideline]:
        pass
