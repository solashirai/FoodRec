from food_rec.services.guideline import GraphGuidelineKgQueryService
from frex.stores import LocalGraph
from pathlib import Path
from typing import Tuple


class LocalGraphGuidelineKgQueryService(GraphGuidelineKgQueryService):
    """
    A graph-based GuidelineKG query service using a locally stored graph.
    """

    def __init__(self, *, file_paths: Tuple[Path]):
        queryable = LocalGraph(file_paths=file_paths)
        super().__init__(queryable=queryable)
