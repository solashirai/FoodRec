from food_rec.utils.namespace import *
from food_rec.models import *
from food_rec.services.graph import _GraphQueryService
from food_rec.services.user import UserKgQueryService
from rdflib import URIRef, Graph
from food_rec.utils import J2QueryStrService
from food_rec.services.exceptions import *


class GraphUserKgQueryService(_GraphQueryService, UserKgQueryService):
    def get_user_by_uri(self, *, user_uri: URIRef) -> FoodKgUser:
        """
        Query the User KG to retrieve a FoodKGUser object with the target URI.

        :param user_uri: the URI of the user to return
        :return: a FoodKGUser object with the target URI
        """
        res_graph = self.get_cache_graph(
            sparql=J2QueryStrService.j2_query(
                file_name="construct_user_query",
                constraints=[{"var_name": "?userUri", "var_values": [user_uri.n3()]}],
            )
        )
        user = self._graph_get_user_by_uri(user_uri=user_uri)

        return user

    def _graph_get_user_by_uri(self, *, user_uri: URIRef) -> FoodKgUser:
        """
        Retrieve a target user by their URI from the graph

        :param user_uri: target user URI
        :raises: MalformedUserException, UserNotFoundException
        :return: a FoodKgUser of the target user
        """
        if (user_uri, None, None) not in self.cache_graph:
            raise UserNotFoundException(user_uri=user_uri)

        name = self.cache_graph.value(user_uri, FOOD_KG_USER_NS["user_name"]).value
        sex = self.cache_graph.value(user_uri, FOOD_KG_USER_NS["user_sex"]).value
        if not name:
            raise MalformedUserException(user_uri=user_uri)
        age = self.cache_graph.value(user_uri, FOOD_KG_USER_NS["user_age"])
        if age:
            age = age.value
        bmi = self.cache_graph.value(user_uri, FOOD_KG_USER_NS["user_bmi"])
        if bmi:
            bmi = bmi.value

        favorite_recipe_set = {
            recipe_uri
            for recipe_uri in self.cache_graph.objects(
                user_uri, FOOD_KG_USER_NS["favorite_recipe"]
            )
        }
        prohibited_ing_set = {
            ing_uri
            for ing_uri in self.cache_graph.objects(
                user_uri, FOOD_KG_USER_NS["prohibited_ingredient"]
            )
        }
        prohibited_foodon_set = set()
        nutrition_constraint_set = set()
        for diet_restriction in self.cache_graph.objects(
            user_uri, FOOD_KG_USER_NS["user_dietary_restriction"]
        ):
            prohibited_foodon_set = prohibited_foodon_set.union(
                {
                    foodon_class_uri
                    for foodon_class_uri in self.cache_graph.objects(
                        diet_restriction,
                        FOOD_KG_DIET_REST_NS["restricted_foodon_class"],
                    )
                }
            )

            # TODO: this will likely become more complicated in the future. currently just using single string.
            nutrition_constraint_set = nutrition_constraint_set.union(
                {
                    nutrition_con.value
                    for nutrition_con in self.cache_graph.objects(
                        diet_restriction,
                        FOOD_KG_DIET_REST_NS["nutrition_constraint"],
                    )
                }
            )
        available_ing_set = {
            ing_uri
            for ing_uri in self.cache_graph.objects(
                user_uri, FOOD_KG_USER_NS["available_ingredient"]
            )
        }
        lifestyle_guideline_set = {
            lifestyle_uri
            for lifestyle_uri in self.cache_graph.objects(
                user_uri, FOOD_KG_USER_NS["target_lifestyle_guideline"]
            )
        }

        # TODO: User currently expects sets of recipes/ingredients. if we're assuming user_kg and food_kg could be
        #  separate, we can't convert the URIs to food_kg classes here
        return FoodKgUser(
            uri=user_uri,
            name=name,
            sex=sex,
            age=age,
            bmi=bmi,
            favorite_recipe_uri_set=frozenset(favorite_recipe_set),
            prohibited_ingredient_uri_set=frozenset(prohibited_ing_set),
            prohibited_foodon_class_set=frozenset(prohibited_foodon_set),
            nutrition_constraint_set=frozenset(nutrition_constraint_set),
            target_lifestyle_guideline_set=frozenset(lifestyle_guideline_set),
            available_ingredient_uri_set=frozenset(available_ing_set),
        )
