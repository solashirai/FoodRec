from food_rec.services.food import GraphFoodKgQueryService
from frex.stores import RemoteGraph


class RemoteGraphFoodKgQueryService(GraphFoodKgQueryService):
    """
    A graph-based FoodKG query service using a remote endpoint to store the graph.
    """

    def __init__(self, *, sparql_endpoint: str):
        queryable = RemoteGraph(endpoint=sparql_endpoint)
        super().__init__(queryable=queryable)
