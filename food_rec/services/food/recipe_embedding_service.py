import numpy as np
import pickle
import json
from typing import List, Tuple, Dict


class RecipeEmbeddingService:
    """
    A service to handle converting recipes into vectors, based on pre-trained recipe embeddings.
    Currently set up to use embeddings developed by Diya.
    """

    def __init__(self, *, embedding_file: str, id_file: str):
        with open(embedding_file, "rb") as f:
            self.ingre_emb_val = pickle.load(f)
        with open(id_file, "rb") as f:
            self.rec_id_val = pickle.load(f)
        self.id_to_embedding_dict = {
            k: v for k, v in zip(self.rec_id_val, self.ingre_emb_val)
        }

    def get_recipe_embedding(self, *, recipe_id: str) -> np.array:
        """
        Retrieve the embedding for a particular recipe ID.

        :param recipe_id: the ID (from recipe1m) of the recipe to get the embedding for
        :return: A numpy array representing the embedding for the target recipe
        """
        recipe_index = np.where(self.rec_id_val == recipe_id)
        if len(recipe_index[0]) == 0:
            return None

        return self.ingre_emb_val[recipe_index[0][0]]
