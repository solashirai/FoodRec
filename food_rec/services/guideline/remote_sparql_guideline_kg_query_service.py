from food_rec.services.guideline import GraphGuidelineKgQueryService
from frex.stores import RemoteGraph


class RemoteGraphGuidelineKgQueryService(GraphGuidelineKgQueryService):
    """
    A graph-based Guideline KG query service using a remote sparql endpoint.
    """

    def __init__(self, *, sparql_endpoint: str):
        queryable = RemoteGraph(endpoint=sparql_endpoint)
        super().__init__(queryable=queryable)
