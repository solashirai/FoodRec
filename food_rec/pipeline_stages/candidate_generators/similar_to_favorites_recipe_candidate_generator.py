from frex import CandidateGenerator, Explanation, Candidate
from typing import Generator, Dict, Tuple
from food_rec.models import FoodKgRecipe
from food_rec.services.food import FoodKgQueryService
from food_rec.services.food import RecipeEmbeddingService
from food_rec.models import PatientContext, RecipeCandidate
from frex.utils import VectorSimilarityUtils
import numpy as np
import copy


class SimilarToFavoritesRecipeCandidateGenerator(CandidateGenerator):
    """
    Generate recipe candidates that are similar to a patient's favorite recipes.
    """

    context: PatientContext

    def __init__(
        self,
        *,
        recipe_embedding_service: RecipeEmbeddingService,
        food_kg_query_service: FoodKgQueryService,
        **kwargs,
    ):
        self.res = recipe_embedding_service
        self.fqs = food_kg_query_service
        generator_explanation = None
        CandidateGenerator.__init__(
            self, generator_explanation=generator_explanation, **kwargs
        )

    def generate(
        self,
        *,
        candidates: Generator[Candidate, None, None] = None,
        context: PatientContext,
    ) -> Generator[RecipeCandidate, None, None]:
        if candidates:
            yield from candidates

        favorite_recipe_uris = context.target_user.favorite_recipe_uri_set

        fav_recipes = [
            self.fqs.get_recipe_by_uri(recipe_uri=recipe_uri)
            for recipe_uri in favorite_recipe_uris
        ]
        fav_recipe_ids = {rec.id for rec in fav_recipes}
        uri_ids = self.fqs.get_all_recipe_uris_and_ids()

        valid_recipe_ids = {
            uri_id[1] for uri_id in uri_ids if uri_id[1] not in fav_recipe_ids
        }

        recipe_sim_dict: Dict[str, Tuple[float, FoodKgRecipe]] = dict()
        for fav_recipe in fav_recipes:
            fav_id = fav_recipe.id

            id_emb_dict = copy.copy(self.res.id_to_embedding_dict)
            fav_embedding = id_emb_dict.pop(fav_id).reshape(1, -1)

            comparison_ids = []
            comparison_embeddings = []

            for key, val in id_emb_dict.items():
                if np.sum(val) == 0:  # np.sum(val) == 600 or
                    continue
                if key in valid_recipe_ids:
                    comparison_ids.append(key)
                    comparison_embeddings.append(val.reshape(1, -1))

            recipe_sim_scores = VectorSimilarityUtils.get_item_vector_similarity(
                target_item=fav_id,
                target_vector=fav_embedding,
                comparison_items=comparison_ids,
                comparison_contents=comparison_embeddings,
            )

            print("number of recipes getting compared: ", len(comparison_ids))

            sim_rec_id_score = VectorSimilarityUtils.get_top_n_candidates(
                candidate_score_dict=recipe_sim_scores, top_n=100
            )

            for rec_id, sim_score in sim_rec_id_score:
                if rec_id in recipe_sim_dict:
                    if sim_score > recipe_sim_dict[rec_id][0]:
                        recipe_sim_dict[rec_id] = (sim_score, fav_recipe)
                else:
                    recipe_sim_dict[rec_id] = (sim_score, fav_recipe)

        for rec_id in recipe_sim_dict.keys():
            sim_score, fav_recipe = recipe_sim_dict[rec_id]
            yield RecipeCandidate(
                context=context,
                domain_object=self.fqs.get_recipe_by_uri(
                    recipe_uri=self.fqs.get_recipe_uri_by_recipe1m_id(recipe_id=rec_id)
                ),
                applied_explanations=[
                    Explanation(
                        explanation_string=f"This recipe had a similarity score of {sim_score} "
                        f"to one of your favorite recipes, {fav_recipe.name}."
                    )
                ],
                applied_scores=[sim_score],
            )
