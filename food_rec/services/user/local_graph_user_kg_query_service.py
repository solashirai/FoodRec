from typing import Tuple
from food_rec.services.user import GraphUserKgQueryService
from pathlib import Path
from frex.stores import LocalGraph


class LocalGraphUserKgQueryService(GraphUserKgQueryService):
    """
    A graph-based User KG query service using a locally stored graph.
    """

    def __init__(self, *, file_paths: Tuple[Path]):
        queryable = LocalGraph(file_paths=file_paths)
        super().__init__(queryable=queryable)
