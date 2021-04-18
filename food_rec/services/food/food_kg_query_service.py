from abc import ABC, abstractmethod
from rdflib import Graph, URIRef
from typing import Dict, Tuple, Set, Tuple
from food_rec.models import *


class FoodKgQueryService(ABC):
    @abstractmethod
    def get_recipe_by_uri(self, *, recipe_uri: URIRef) -> FoodKgRecipe:
        pass

    @abstractmethod
    def get_recipes_by_uri(self, *, recipe_uris: Tuple[URIRef]) -> Tuple[FoodKgRecipe]:
        pass

    @abstractmethod
    def get_all_recipes(self) -> Tuple[FoodKgRecipe]:
        pass

    @abstractmethod
    def get_all_recipe_uris_and_ids(self) -> Tuple[Tuple[URIRef, str]]:
        pass

    @abstractmethod
    def get_recipe_uris_and_ids_using_any_ingredients(
        self, *, ingredient_uris: Set[URIRef]
    ) -> Tuple[Tuple[URIRef, str]]:
        pass

    @abstractmethod
    def get_recipe_uris_and_ids_using_all_ingredients(
        self, *, ingredient_uris: Set[URIRef]
    ) -> Tuple[Tuple[URIRef, str]]:
        pass

    @abstractmethod
    def get_recipe_uris_and_ids_not_using_ingredients(
        self, *, prohibited_ingredient_uris: Set[URIRef]
    ) -> Tuple[Tuple[URIRef, str]]:
        pass

    @abstractmethod
    def get_recipe_total_calories_by_uris(
        self, *, recipe_uris: Tuple[URIRef]
    ) -> Dict[URIRef, float]:
        pass

    @abstractmethod
    def get_recipe_total_sodium_by_uris(
        self, *, recipe_uris: Tuple[URIRef]
    ) -> Dict[URIRef, float]:
        pass

    @abstractmethod
    def get_ingredient_uris_by_recipe_uris(
        self, *, recipe_uris: Tuple[URIRef]
    ) -> Dict[URIRef, Set[URIRef]]:
        pass

    @abstractmethod
    def get_recipe_uri_by_recipe1m_id(self, *, recipe_id: str) -> URIRef:
        pass

    @abstractmethod
    def get_ingredient_use_by_uri(self, *, ing_use_uri: URIRef) -> FoodKgIngredientUse:
        pass

    @abstractmethod
    def get_ingredient_by_uri(self, *, ing_uri: URIRef) -> FoodKgIngredient:
        pass

    @abstractmethod
    def get_usda_nutrition_by_uri(self, *, usda_uri: URIRef) -> NutritionInfo:
        pass

    @abstractmethod
    def get_simple_substitutions_by_ingredient_uri(
        self, *, ing_uri: URIRef
    ) -> Tuple[FoodKgIngredientSubstitutionOption]:
        pass

    @abstractmethod
    def get_simple_substitutions_by_recipe_uri(
        self, *, recipe_uri: URIRef
    ) -> Tuple[FoodKgIngredientSubstitutionOption]:
        pass

    @abstractmethod
    def get_all_recipes_not_using_ingredients(
        self, *, prohibited_ing_uris: Set[URIRef]
    ) -> Tuple[FoodKgRecipe]:
        pass

    @abstractmethod
    def get_all_recipes_not_using_foodon_subclasses(
        self, *, prohibited_foodon_uris: Set[URIRef]
    ) -> Tuple[FoodKgRecipe]:
        pass
