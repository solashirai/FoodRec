from food_rec.services.user import GraphUserKgQueryService
from frex.stores import RemoteGraph


class RemoteGraphUserKgQueryService(GraphUserKgQueryService):
    """
    A graph-based User KG query service using a remote sparql endpoint.
    """

    def __init__(self, *, sparql_endpoint: str):
        queryable = RemoteGraph(endpoint=sparql_endpoint)
        super().__init__(queryable=queryable)
