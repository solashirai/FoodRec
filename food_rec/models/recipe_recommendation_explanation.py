from food_rec.models import Guideline
from typing import Tuple, NamedTuple
from frex import Explanation


class RecipeRecommendationExplanation(Explanation, NamedTuple):
    """
    Class to store explanation information for a recipe recommendation.

    The explanation currently consists of a number of explanations that were applied through
    the course of the recommendation pipeline, typically from pipeline stages.
    """

    explanation_contents: Tuple[Explanation, ...]

    @property
    def explanation_string(self) -> str:
        if len(self.explanation_contents) > 0:
            output_str = "Applied guideline explanations: "
            output_str += " : ".join(
                explanation.get_explanation_string()
                for explanation in self.explanation_contents
            )
        else:
            output_str = "No guidelines applied"
        return output_str
