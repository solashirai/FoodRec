from food_rec.services import LocalGraphFoodKgQueryService
from food_rec.services import GraphExplainableFoodRecommenderService
from food_rec.models import *
import pytest
from frex.models import Explanation


def test_get_meal_plan_for_user(
    food_kg_rec: GraphExplainableFoodRecommenderService,
    food_kg: LocalGraphFoodKgQueryService,
    test_user: FoodKgUser,
    placeholder_guideline: Guideline,
    test_ingredient_vars,
):
    mp = food_kg_rec.get_meal_plan_for_user(
        user=test_user, number_of_days=3, meals_per_day=1
    )

    expected_mp_rec = MealPlanRecommendation(
        meal_plan_days=(
            MealPlanDay(
                recipe_recommendations=(
                    RecipeRecommendation(
                        recipe=food_kg.get_recipe_by_uri(
                            recipe_uri=test_ingredient_vars.gratin_potato_recipe_uri
                        ),
                        explanation=RecipeRecommendationExplanation(
                            explanation_contents=(
                                Explanation(
                                    explanation_string="This recipe had a similarity score of 0.012105363142076218 "
                                    "to one of your favorite recipes, Lamb Chops au Gratin."
                                ),
                                Explanation(
                                    explanation_string="This recipe does not contain any ingredients that are prohibited by you."
                                ),
                                Explanation(
                                    explanation_string="Adheres to guideline: As for the general population, people with "
                                    "diabetes should limit sodium consumption to <2,300 mg/day."
                                ),
                                Explanation(
                                    explanation_string="Scoring based on calories, this is mostly a placeholder to break ties."
                                ),
                            )
                        ),
                    ),
                ),
                explanation=Explanation(
                    explanation_string=f"This is a set of recommended recipes to eat for this day, "
                    f"based on suggesting recipes that you are likely to like in general."
                ),
            ),
            MealPlanDay(
                recipe_recommendations=(
                    RecipeRecommendation(
                        recipe=food_kg.get_recipe_by_uri(
                            recipe_uri=test_ingredient_vars.layer_din_recipe_uri
                        ),
                        explanation=RecipeRecommendationExplanation(
                            explanation_contents=(
                                Explanation(
                                    explanation_string="This recipe had a similarity score of 1.0 "
                                    "to one of your favorite recipes, Lamb Chops au Gratin."
                                ),
                                Explanation(
                                    explanation_string="This recipe does not contain any ingredients that are prohibited by you."
                                ),
                                Explanation(
                                    explanation_string="Does not adhere to guideline: As for the general population, people with "
                                    "diabetes should limit sodium consumption to <2,300 mg/day."
                                ),
                                Explanation(
                                    explanation_string="Scoring based on calories, this is mostly a placeholder to break ties."
                                ),
                            )
                        ),
                    ),
                ),
                explanation=Explanation(
                    explanation_string=f"This is a set of recommended recipes to eat for this day, "
                    f"based on suggesting recipes that you are likely to like in general."
                ),
            ),
            MealPlanDay(
                recipe_recommendations=(
                    RecipeRecommendation(
                        recipe=food_kg.get_recipe_by_uri(
                            recipe_uri=test_ingredient_vars.amish_soup_recipe_uri
                        ),
                        explanation=RecipeRecommendationExplanation(
                            explanation_contents=(
                                Explanation(
                                    explanation_string="This recipe had a similarity score of 1.0 "
                                    "to one of your favorite recipes, Lamb Chops au Gratin."
                                ),
                                Explanation(
                                    explanation_string="This recipe does not contain any ingredients that are prohibited by you."
                                ),
                                Explanation(
                                    explanation_string="Does not adhere to guideline: As for the general population, people with "
                                    "diabetes should limit sodium consumption to <2,300 mg/day."
                                ),
                                Explanation(
                                    explanation_string="Scoring based on calories, this is mostly a placeholder to break ties."
                                ),
                            )
                        ),
                    ),
                ),
                explanation=Explanation(
                    explanation_string=f"This is a set of recommended recipes to eat for this day, "
                    f"based on suggesting recipes that you are likely to like in general."
                ),
            ),
        ),
        explanation=Explanation(
            explanation_string=f"This is a meal plan that was generated for 3 days of meals,"
            f" eating 1 meals each day."
        ),
    )

    assert (
        frozenset(mp.domain_object.meal_plan_days)
        == frozenset(expected_mp_rec.meal_plan_days)
        and mp.domain_object.explanation == expected_mp_rec.explanation
    )
