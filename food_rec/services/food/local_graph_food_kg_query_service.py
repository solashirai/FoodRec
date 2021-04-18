from typing import Tuple
from pathlib import Path
from food_rec.services.food import GraphFoodKgQueryService
from frex.stores import LocalGraph


class LocalGraphFoodKgQueryService(GraphFoodKgQueryService):
    """
    A graph-based FoodKG query service using a locally stored graph.
    """

    def __init__(self, *, file_paths: Tuple[Path]):
        queryable = LocalGraph(file_paths=file_paths)
        super().__init__(queryable=queryable)
