from food_rec.utils.namespace import *
from food_rec.models import *
from typing import Set, Tuple, Dict
from collections import defaultdict
from rdflib import URIRef, Graph, Literal
from food_rec.utils import cfg, FoodKgInredientUseParser, FoodKgNutritionParser
from food_rec.services.exceptions import *
from food_rec.services.graph import _GraphQueryService
from food_rec.services.food import FoodKgQueryService
from food_rec.utils import J2QueryStrService
import stringcase


class GraphFoodKgQueryService(_GraphQueryService, FoodKgQueryService):
    """
    A query service for a FoodKG stored as a graph.
    Queries of the form get_X_by_uri will typically first use sparql to query the graph,
    then the returned result is cached to retrieve subsequent domain objects.

    Queries should be made at the highest level possible to help reduce the number of sparql queries
    that are performed (e.g. rather than repeatedly querying to get_recipe_by_uri for multiple recipes,
    use get_recipes_by_uri, so that one sparql query is called to cache a graph of all relevant recipes).
    """

    def get_recipe_by_uri(self, *, recipe_uri: URIRef) -> FoodKgRecipe:
        """
        Query the FoodG and return a FoodKgRecipe object with the given uri

        :param recipe_uri: URI of the recipe
        :return: the target FoodKgRecipe object
        """
        self.get_cache_graph(
            sparql=J2QueryStrService.j2_query(
                file_name="construct_recipe_query",
                constraints=[
                    {"var_name": "?recipeUri", "var_values": [recipe_uri.n3()]}
                ],
            )
        )
        recipe = self._graph_get_recipe_by_uri(recipe_uri=recipe_uri)

        return recipe

    def get_recipes_by_uri(self, *, recipe_uris: Tuple[URIRef]) -> Tuple[FoodKgRecipe]:
        """
        Query the FoodG and return a tuple of FoodKgRecipe objects with the given uris

        :param recipe_uris: URIs of the recipes to retrieve
        :return: a tuple of the target FoodKgRecipe objects
        """
        self.get_cache_graph(
            sparql=J2QueryStrService.j2_query(
                file_name="construct_recipe_query",
                constraints=[
                    {
                        "var_name": "?recipeUri",
                        "var_values": [recipe_uri.n3() for recipe_uri in recipe_uris],
                    }
                ],
            )
        )
        recipes = tuple(
            self._graph_get_recipe_by_uri(recipe_uri=recipe_uri)
            for recipe_uri in recipe_uris
        )

        return recipes

    def get_all_recipes(self) -> Tuple[FoodKgRecipe]:
        """
        Query the FoodKG and return objects for all FoodKGRecipes present in the graph

        :return: A tuple of all available FoodKgRecipes
        """
        self.get_cache_graph(
            sparql=J2QueryStrService.j2_query(file_name="construct_recipe_query")
        )

        return self._graph_get_all_recipes()

    def get_all_recipe_uris_and_ids(self) -> Tuple[Tuple[URIRef, str]]:
        """
        Query the FoodKG and return all URIs and IDs of recipes present in the graph

        :return: A tuple of tuples, where each inner tuple is the URI and Recipe1M ID of a recipe
        """
        query = self.get_query_result(
            sparql=J2QueryStrService.j2_query(
                file_name="select_all_recipe_uris_and_ids"
            )
        )

        return tuple([(res.recipeUri, res.recipeId.value) for res in query])

    def get_recipe_uris_and_ids_using_any_ingredients(
        self, *, ingredient_uris: Set[URIRef]
    ) -> Tuple[Tuple[URIRef, str]]:
        """
        Query the FoodKG to get recipe URIs and ID for all recipes that use at least 1 ingredient from
        the input set of ingredient URis.

        :param ingredient_uris: A set of ingredient URIs that output recipes must use
        :return: A tuple of tuples, where the inner tuple is the URI and Recipe1M ID of recipes that use
        at least 1 ingredient found in the ingredient_uris set
        """
        query = self.get_query_result(
            sparql=J2QueryStrService.j2_query(
                file_name="select_recipe_uris_and_ids_using_any_ings_query",
                constraints=[
                    {
                        "var_name": "?ingUri",
                        "var_values": [ing_uri.n3() for ing_uri in ingredient_uris],
                    }
                ],
            )
        )
        return tuple([(res.recipeUri, res.recipeId.value) for res in query])

    def get_recipe_uris_and_ids_using_all_ingredients(
        self, *, ingredient_uris: Set[URIRef]
    ) -> Tuple[Tuple[URIRef, str]]:
        """
        Query the FoodKG to get recipe URIs and ID for all recipes that use all of the ingredient in
        the input set of ingredient URis.

        :param ingredient_uris: A set of ingredient URIs that output recipes must use
        :return: A tuple of tuples, where the inner tuple is the URI and Recipe1M ID of recipes that use
        all ingredient found in the ingredient_uris set
        """

        query = self.get_query_result(
            sparql=J2QueryStrService.j2_query(
                file_name="select_recipe_uris_and_ids_using_all_ings_query",
                constraints=[
                    {
                        "var_name": "?ingUri",
                        "var_values": [ing_uri.n3() for ing_uri in ingredient_uris],
                    }
                ],
            )
        )
        return tuple([(res.recipeUri, res.recipeId.value) for res in query])

    def get_recipe_uris_and_ids_not_using_ingredients(
        self, *, prohibited_ingredient_uris: Set[URIRef]
    ) -> Tuple[Tuple[URIRef, str]]:
        """
        Query the graph to get recipe URIs and ID for all recipes that do not use any ingredients from
        the input set of ingredient URis.

        :param prohibited_ingredient_uris: A set of ingredient URIs that output recipes must not use
        :return: A tuple of tuples, where the inner tuple is the URI and Recipe1M ID of recipes that do
        not use any ingredient found in the ingredient_uris set
        """
        if prohibited_ingredient_uris:
            constraints = [
                {
                    "var_name": "?prohibIngUri",
                    "var_values": [
                        ing_uri.n3() for ing_uri in prohibited_ingredient_uris
                    ],
                }
            ]
        else:
            constraints = [{"var_name": "?prohibIngUri", "var_values": ["<>"]}]
        query = self.get_query_result(
            sparql=J2QueryStrService.j2_query(
                file_name="select_recipe_uris_and_ids_not_using_ings_query",
                constraints=constraints,
            )
        )

        return tuple([(res.recipeUri, res.recipeId.value) for res in query])

    def get_recipe_total_calories_by_uris(
        self, *, recipe_uris: Tuple[URIRef]
    ) -> Dict[URIRef, float]:
        """
        Query the FoodKG and retrieve the total calories found in recipes

        :param recipe_uris: A tuple of recipe URIs to retrieve calorie information for
        :return: A dictionary of recipe URIs to their corresponding calorie counts
        """
        query = self.get_query_result(
            sparql=J2QueryStrService.j2_query(
                file_name="select_recipe_total_calories",
                constraints=[
                    {
                        "var_name": "?recipeUri",
                        "var_values": [recipe_uri.n3() for recipe_uri in recipe_uris],
                    }
                ],
            )
        )
        rec_cal_dict = dict()
        if query:
            rec_cal_dict = {res.recipeUri: res.recipeCals.value for res in query}
        return rec_cal_dict

    def get_recipe_total_sodium_by_uris(
        self, *, recipe_uris: Tuple[URIRef]
    ) -> Dict[URIRef, float]:
        """
        Query the FoodKG and retrieve the total sodium found in recipes

        :param recipe_uris: A tuple of recipe URIs to retrieve sodium information for
        :return: A dictionary of recipe URIs to their corresponding sodium
        """
        query = self.get_query_result(
            sparql=J2QueryStrService.j2_query(
                file_name="select_recipe_total_sodium",
                constraints=[
                    {
                        "var_name": "?recipeUri",
                        "var_values": [recipe_uri.n3() for recipe_uri in recipe_uris],
                    }
                ],
            )
        )
        rec_sod_dict = dict()
        if query:
            rec_sod_dict = {res.recipeUri: res.recipeSod.value for res in query}
        return rec_sod_dict

    def get_ingredient_uris_by_recipe_uris(
        self, *, recipe_uris: Tuple[URIRef]
    ) -> Dict[URIRef, Set[URIRef]]:
        """
        Query the FoodKG to retrieve URIs of all ingredients that recipes use.

        :param recipe_uris: A tuple of recipe URIs for which we want to retrieve ingredient URI information
        :return: A dictionary of recipe URIs to a set of ingredient URis that the recipe uses
        """
        query = self.get_query_result(
            sparql=J2QueryStrService.j2_query(
                file_name="select_recipe_ing_uris",
                constraints=[
                    {
                        "var_name": "?recipeUri",
                        "var_values": [recipe_uri.n3() for recipe_uri in recipe_uris],
                    }
                ],
            )
        )
        rec_ing_dict = defaultdict(lambda: set())
        for res in query:
            rec_ing_dict[res.recipeUri].add(res.ingUri)
        return dict(rec_ing_dict)

    def get_recipe_uri_by_recipe1m_id(self, *, recipe_id: str) -> URIRef:
        """
        Query the FoodKG and retrieve a recipe URI associated with its recipe1M ID

        :param recipe_id: the recipe1M ID of the target recipe
        :return: the URI of the target recipe
        """
        query = self.get_query_result(
            sparql=J2QueryStrService.j2_query(
                file_name="select_recipe_uri_by_id",
                constraints=[
                    {"var_name": "?recipeId", "var_values": [Literal(recipe_id).n3()]}
                ],
            )
        )

        # expecting exactly 1 recipe
        return [res.recipeUri for res in query][0]

    def get_ingredient_use_by_uri(self, *, ing_use_uri: URIRef) -> FoodKgIngredientUse:
        """
        Query the FoodKG and return a FoodKgIngredientUse object by its URI

        :param ing_use_uri: the uri of the ingredient use to retrieve
        :return: a FoodKGIngredientUse object for the target URI
        """
        self.get_cache_graph(
            sparql=J2QueryStrService.j2_query(
                file_name="construct_ingredient_use_query",
                constraints=[
                    {"var_name": "?ingUseUri", "var_values": [ing_use_uri.n3()]}
                ],
            )
        )
        ing_use = self._graph_get_ingredient_use_by_uri(ing_use_uri=ing_use_uri)

        return ing_use

    def get_ingredient_by_uri(self, *, ing_uri: URIRef) -> FoodKgIngredient:
        """
        Query the FoodKG and return a FoodKgIngredient object by its URI

        :param ing_uri: the URI of the ingredient to retrieve
        :return: a FoodKgIngredient object for the target URI
        """
        self.get_cache_graph(
            sparql=J2QueryStrService.j2_query(
                file_name="construct_ingredient_query",
                constraints=[{"var_name": "?ingUri", "var_values": [ing_uri.n3()]}],
            )
        )
        ingredient = self._graph_get_ingredient_by_uri(ing_uri=ing_uri)

        return ingredient

    def get_usda_nutrition_by_uri(self, *, usda_food_uri: URIRef) -> NutritionInfo:
        """
        Query the FoodKG and return the nutrition information for a target usda food uri

        :param usda_food_uri: the URI of the usda food whose nutrition is to be retrieved
        :return: a NutritionInfo object for the target URI
        """
        self.get_cache_graph(
            sparql=J2QueryStrService.j2_query(
                file_name="construct_usda_nutrition_query",
                constraints=[
                    {"var_name": "?usdaUri", "var_values": [usda_food_uri.n3()]}
                ],
            )
        )
        nutrition_inf = self._graph_get_nutritional_info_by_uri(
            usda_food_uri=usda_food_uri
        )

        return nutrition_inf

    def get_simple_substitutions_by_ingredient_uri(
        self, *, ing_uri: URIRef
    ) -> Tuple[FoodKgIngredientSubstitutionOption]:
        """
        Query the FoodKG to retrieve simple substitutions for a target ingredient based on its URI

        :param ing_uri: the URI of the target ingredient to retrieve substitutions for
        :return: A tuple of substitution options objects
        """
        self.get_cache_graph(
            sparql=J2QueryStrService.j2_query(
                file_name="construct_simple_substitutions_query",
                constraints=[{"var_name": "?fromIngUri", "var_values": [ing_uri.n3()]}],
            )
        )
        sub_options = self._graph_get_simple_substitutions_by_ingredient_uri(
            ing_uri=ing_uri
        )

        return sub_options

    def get_simple_substitutions_by_recipe_uri(
        self, *, recipe_uri: URIRef
    ) -> Tuple[FoodKgIngredientSubstitutionOption]:
        """
        Query the FoodKG to retrieve all simple substitutions that can be applied to ingredients found
        in a recipe, based on the recipe's URI

        :param recipe_uri: the URI of the target recipe for which we must retrieve ingredients and find substitutions
        :return: A tuple of ingredient substitution options that cover all ingredients in the recipe
        """
        self.get_cache_graph(
            sparql=J2QueryStrService.j2_query(
                file_name="construct_recipe_simple_substitutions_query",
                constraints=[
                    {"var_name": "?recipeUri", "var_values": [recipe_uri.n3()]}
                ],
            )
        )
        sub_options = self._graph_get_recipe_simple_substitutions_by_recipe_uri(
            recipe_uri=recipe_uri
        )

        return sub_options

    def get_all_recipes_not_using_ingredients(
        self, *, prohibited_ing_uris: Set[URIRef]
    ) -> Tuple[FoodKgRecipe]:
        """
        Query the FoodKG to retrieve all recipes that do not use any of the prohibited ingredients.
        TODO: this query is extremely slow with any reasonably sized KG

        :param prohibited_ing_uris: A set of URIs of ingredients that are prohibited
        :return: A tuple of FoodKGRecipe objects that do not use the prohibited ingredients
        """
        if not prohibited_ing_uris:
            return self.get_all_recipes()

        self.get_cache_graph(
            sparql=J2QueryStrService.j2_query(
                file_name="construct_all_recipes_not_using_ings_query",
                constraints=[
                    {
                        "var_name": "?prohibIngUri",
                        "var_values": [ing_uri.n3() for ing_uri in prohibited_ing_uris],
                    }
                ],
            )
        )

        recipes = self._graph_get_all_recipes()

        return recipes

    def get_all_recipes_not_using_foodon_subclasses(
        self, *, prohibited_foodon_uris: Set[URIRef]
    ) -> Tuple[FoodKgRecipe]:
        """
        Query the FoodKG to retrieve all recipes that do not use any ingredient based on foodon uris.
        The query will first determine all ingredients that are subclasses of the prohibited foodon classes,
        then it will select all recipes that do not use any of those ingredients.

        :param prohibited_foodon_uris: A set of URIs for foodon classes that are prohibited
        :return: A tuple of FoodKGRecipe objects containing no ingredient that is a subclass of the prohibited classes
        """
        if not prohibited_foodon_uris:
            return self.get_all_recipes_not_using_ingredients(prohibited_ing_uris=set())

        prohibited_ing_uri_res = self.get_query_result(
            sparql=J2QueryStrService.j2_query(
                file_name="select_ingredient_uri_related_to_foodon_class_query",
                constraints=[
                    {
                        "var_name": "?foodonClassUri",
                        "var_values": [
                            foodon_uri.n3() for foodon_uri in prohibited_foodon_uris
                        ],
                    }
                ],
            )
        )
        prohibited_ing_uris = set()
        if prohibited_ing_uri_res:
            prohibited_ing_uris = {res.ingUri for res in prohibited_ing_uri_res}
        return self.get_all_recipes_not_using_ingredients(
            prohibited_ing_uris=prohibited_ing_uris
        )

    def _graph_get_usda_food_by_ingredient_uri(self, *, ing_uri: URIRef) -> URIRef:
        """
        Get the USDA nutrition info URI associated with a particular ingredient URI

        :param ing_uri: target ingredient URI to get associated USDA ingredient for
        :raises: UsdaFoodNotFoundException
        :return: URI for a usda ingredient
        """
        usda_food_uri = self.cache_graph.value(
            ing_uri, FOOD_KG_NS["equivalentUsdaFood"]
        )
        if not usda_food_uri:
            raise UsdaFoodNotFoundException(usda_food_uri=usda_food_uri)

        return usda_food_uri

    def _graph_get_nutritional_info_by_uri(
        self, *, usda_food_uri: URIRef
    ) -> NutritionInfo:
        """
        Collect nutritional information for a target ingredient from the USDA graph.

        :param usda_food_uri: USDA ingredient to get nutrition info for
        :raises: UsdaFoodNotFoundException
        :return: a dict of corresponding nutrition info
        """

        if (usda_food_uri, None, None) not in self.cache_graph:
            raise UsdaFoodNotFoundException(usda_food_uri=usda_food_uri)

        nutrition_dict = {}
        for (nutrition_attr, nutrition_val) in self.cache_graph.predicate_objects(
            usda_food_uri
        ):
            if nutrition_val == USDA_ONTO_NS["Food"]:
                continue

            for attr_label in self.cache_graph.objects(
                nutrition_attr, RDFS_NS["label"]
            ):
                lab = str(attr_label.value)
                lab = lab.replace("(", "")
                lab = lab.replace(")", "")
                lab = lab.replace("+", " ")
                lab = stringcase.snakecase(lab)
                if not isinstance(nutrition_val.value, str):
                    nutrition_dict[lab] = round(nutrition_val.value, 6)
                else:
                    nutrition_dict[lab] = nutrition_val.value
        return NutritionInfo(**nutrition_dict)

    def _graph_get_ingredient_by_uri(self, *, ing_uri: URIRef) -> FoodKgIngredient:
        """
        Retrieve ingredient information from FoodKG and USDA. The URI should be specific to an ingredient, not a
        particular use of an ingredient in a recipe.

        :param ing_uri: a URI for the target FoodKG ingredient
        :raises: MalformedIngredientException, IngredientNotFoundException
        :return: A new FoodKgIngredient object or none
        """
        if (ing_uri, None, None) not in self.cache_graph:
            raise IngredientNotFoundException(ing_uri=ing_uri)

        ing_label = self.cache_graph.value(ing_uri, RDFS_NS["label"]).value
        if not ing_label:
            raise MalformedIngredientException(ing_uri=ing_uri)

        try:
            usda_equiv = self._graph_get_usda_food_by_ingredient_uri(ing_uri=ing_uri)
            nutrition_inf = self._graph_get_nutritional_info_by_uri(
                usda_food_uri=usda_equiv
            )
        except UsdaFoodNotFoundException:
            usda_equiv = None
            nutrition_inf = NutritionInfo()

        return FoodKgIngredient(
            uri=ing_uri,
            label=ing_label,
            usda_equiv=usda_equiv,
            nutrition_info=nutrition_inf,
        )

    def _graph_get_ingredient_use_by_uri(
        self, *, ing_use_uri: URIRef
    ) -> FoodKgIngredientUse:
        """
        Create an object for a particular ingredient use's URI.

        :param ing_use_uri: the target ingredient use to get
        :raises: MalformedIngredientUseException, IngredientUseNotFoundException
        :return: a FoodKgIngredientUse object
        """
        if (ing_use_uri, None, None) not in self.cache_graph:
            raise IngredientUseNotFoundException(ing_use_uri=ing_use_uri)

        ing_uri = self.cache_graph.value(ing_use_uri, FOOD_KG_NS["ing_name"])
        if not ing_uri:
            raise MalformedIngredientUseException(ing_use_uri=ing_use_uri)

        ingred = self._graph_get_ingredient_by_uri(ing_uri=ing_uri)
        unit = self.cache_graph.value(
            ing_use_uri, FOOD_KG_NS["ing_unit"], default=Literal("")
        ).value
        unit = unit.replace(".", "")
        quant = self.cache_graph.value(ing_use_uri, FOOD_KG_NS["ing_quantity"]).value
        quant = FoodKgInredientUseParser.parse_ingredient_use_quantity(
            quant=quant, unit=unit
        )
        gram_quant = self.cache_graph.value(
            ing_use_uri,
            FOOD_KG_NS["ing_computed_gram_quantity"],
            default=Literal(0),
        ).value
        total_nutrition = FoodKgNutritionParser.compute_total_nutrition_info(
            ingred.nutrition_info, gram_quant
        )
        return FoodKgIngredientUse(
            uri=ing_use_uri,
            foodkg_quantity=quant,
            quantity_units=unit,
            ingredient=ingred,
            gram_quantity=gram_quant,
            total_nutrition_info=total_nutrition,
        )

    def _graph_get_ingredient_uses_by_recipe_uri(
        self, *, recipe_uri: URIRef
    ) -> Set[FoodKgIngredientUse]:
        """
        Get all ingredient uses in a target recipe.

        :param recipe_uri: target recipe to collect ingredientuses
        :return: a set of FoodKgIngredientUse objects corresponding to ingredientuses for the target recipe
        """
        return {
            self._graph_get_ingredient_use_by_uri(ing_use_uri=uri)
            for uri in self.cache_graph.objects(recipe_uri, FOOD_KG_NS["uses"])
        }

    def _graph_get_recipe_by_uri(self, *, recipe_uri: URIRef) -> FoodKgRecipe:
        """
        Check that the FoodKgGrpah contains a recipe then return the corresponding FoodKgrecipe object

        :param recipe_uri: URI of the recipe
        :raises: MalformedRecipeException, RecipeNotFoundException
        :return: the target FoodKgRecipe object
        """
        if (recipe_uri, None, None) not in self.cache_graph:
            raise RecipeNotFoundException(recipe_uri=recipe_uri)

        recipe_id = self.cache_graph.value(recipe_uri, FOOD_KG_NS["recipe1MId"])
        if not recipe_id:
            recipe_id = None
        else:
            recipe_id = recipe_id.value
        recipe_label = self.cache_graph.value(recipe_uri, RDFS_NS["label"])
        if not recipe_label:
            raise MalformedRecipeException(recipe_uri=recipe_uri)
        try:
            ing_uses = self._graph_get_ingredient_uses_by_recipe_uri(
                recipe_uri=recipe_uri
            )
            if not ing_uses:
                raise MalformedRecipeException(
                    recipe_uri=recipe_uri,
                    message=f"Recipe's ingredient uses not found: {recipe_uri}",
                )
        except CustomException as exc:
            raise MalformedRecipeException(
                recipe_uri=recipe_uri,
                message=f"{type(exc)} raised by recipe's ingredient uses: {recipe_uri}",
            )

        ingredient_set = frozenset({ing_use.ingredient for ing_use in ing_uses})
        total_nutritional_info = FoodKgRecipe.get_total_nutrition_info(ing_uses)
        ing_uses = frozenset(set(ing_uses))

        return FoodKgRecipe(
            uri=recipe_uri,
            name=recipe_label,
            id=recipe_id,
            ingredient_use_set=ing_uses,
            ingredient_set=ingredient_set,
            total_nutritional_info=total_nutritional_info,
        )

    def _graph_get_all_recipes(self) -> Tuple[FoodKgRecipe]:
        """
        Get all recipes in the current graph.

        :return: A list of all FoodKgRecipes present int he current graph
        """
        recipes = []
        for (recipe_uri, _, _) in self.cache_graph.triples(
            (None, RDF_NS["type"], FOOD_KG_NS["recipe"])
        ):
            recipes.append(self._graph_get_recipe_by_uri(recipe_uri=recipe_uri))
        return tuple(recipes)

    def _graph_get_simple_substitutions_by_ingredient_uri(
        self, *, ing_uri: URIRef
    ) -> Tuple[FoodKgIngredientSubstitutionOption]:
        """
        Get simple substitution options for a single ingredient

        :param ing_uri: URI of the ingredient to get simple substitutions for
        :return: A list of FoodKG Ingredient Substitution Option objects for the target ingredient
        """
        try:
            from_ing = self._graph_get_ingredient_by_uri(ing_uri=ing_uri)
        except IngredientNotFoundException as exc:
            raise IngredientNotFoundException(
                ing_uri=ing_uri,
                message=f"{type(exc)} raised by source ingredient for substitutions: {ing_uri}",
            )
        to_ings = [
            self._graph_get_ingredient_by_uri(ing_uri=uri)
            for uri in self.cache_graph.objects(
                ing_uri, FOOD_KG_SUB_NS["hasSubstitute"]
            )
        ]
        sub_options = {
            FoodKgIngredientSubstitutionOption(
                from_ing=from_ing,
                explanation="fake explanation hardcoded sub",
                to_ing=to_ing,
            )
            for to_ing in to_ings
            if to_ing
        }

        return tuple(sub_options)

    def _graph_get_recipe_simple_substitutions_by_recipe_uri(
        self, *, recipe_uri: URIRef
    ) -> Tuple[FoodKgIngredientSubstitutionOption]:
        """
        Get all simple substitutions for ingredients in a target recipe

        :param recipe_uri: URI of the recipe to get all simple substitutions for
        :raises: RecipeNotFoundException
        :return: A list of FoodKG Ingredient Substitution Options for all ingredients in the recipe
        """
        if (recipe_uri, None, None) not in self.cache_graph:
            raise RecipeNotFoundException(
                recipe_uri=recipe_uri,
                message=f"Recipe to get substitutions for not found: {recipe_uri}",
            )

        from_ings = [
            from_ing_uri
            for from_ing_use_uri in self.cache_graph.objects(
                recipe_uri, FOOD_KG_NS["uses"]
            )
            for from_ing_uri in self.cache_graph.objects(
                from_ing_use_uri, FOOD_KG_NS["ing_name"]
            )
        ]

        sub_options = [
            sub_option
            for from_ing in from_ings
            for sub_option in self._graph_get_simple_substitutions_by_ingredient_uri(
                ing_uri=from_ing
            )
        ]

        return tuple(sub_options)
