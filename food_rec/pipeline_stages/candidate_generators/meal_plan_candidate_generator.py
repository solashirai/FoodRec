from frex.models import Explanation, DomainObject
from frex.models.constraints import SectionSetConstraint, ConstraintType
from frex.pipeline_stages import CandidateGenerator
from frex.utils import ConstraintSolver
from typing import Generator, Dict, Tuple
from food_rec.models import FoodKgRecipe
from food_rec.services import ExplainableFoodRecommenderService
from food_rec.models import (
    PatientContext,
    MealPlanCandidate,
    RecipeRecommendationExplanation,
    RecipeRecommendation,
    MealPlanDay,
    MealPlanRecommendation,
    RecipeCandidate,
)
from rdflib import URIRef


class MealPlanCandidateGenerator(CandidateGenerator):
    """
    Generate meal plan candidates using recipes that are similar to a patient's favorite recipes.

    Currently uses the pipeline for recommending recipes to get "good" recipes, and then combine them into
    meal plans for a week (2 meals per day).
    """

    def __init__(
        self,
        number_of_days: int,
        meals_per_day: int,
        **kwargs,
    ):
        self.number_of_days = number_of_days
        self.meals_per_day = meals_per_day

        days = []
        for i in range(self.number_of_days):
            days.append(DomainObject(uri=URIRef(f"placeholderuri.com/{i}")))
        days = tuple(days)

        day_ss = (
            SectionSetConstraint()
            .set_sections(sections=days)
            .add_section_count_constraint(exact_count=self.meals_per_day)
        )
        for day_ind, day in enumerate(days):
            for day2_ind, day2 in enumerate(days[day_ind + 1 :]):
                day_ss.add_section_assignment_constraint(
                    section_a_uri=day.uri,
                    section_b_uri=day2.uri,
                    constraint_type=ConstraintType.AM1,
                )

        self.solver = (
            ConstraintSolver(scaling=100)
            .set_section_set_constraints(section_sets=(day_ss,))
            .add_overall_count_constraint(
                exact_count=self.meals_per_day * self.number_of_days
            )
        )

        generator_explanation = Explanation(
            explanation_string="placeholder hardcoded explanation for a meal plan generation using knapsack problem"
        )
        CandidateGenerator.__init__(
            self, generator_explanation=generator_explanation, **kwargs
        )

    def generate(
        self,
        *,
        candidates: Generator[RecipeCandidate, None, None] = None,
        context: PatientContext,
    ) -> Generator[MealPlanCandidate, None, None]:

        recipe_candidates = tuple(candidates)

        print("ahhhh", len(recipe_candidates))

        soln = self.solver.set_candidates(candidates=recipe_candidates).solve(
            output_uri=URIRef("placeholder.com/placeholder_meal_plan_soln_uri")
        )

        yield MealPlanCandidate(
            context=context,
            applied_scores=[soln.overall_score],
            applied_explanations=[self.generator_explanation],
            domain_object=MealPlanRecommendation(
                explanation=Explanation(
                    explanation_string=f"This is a meal plan that was generated for {self.number_of_days} days of meals,"
                    f" eating {self.meals_per_day} meals each day."
                ),
                meal_plan_days=tuple(
                    MealPlanDay(
                        recipe_recommendations=tuple(
                            RecipeRecommendation(
                                recipe=candidate.domain_object,
                                explanation=RecipeRecommendationExplanation(
                                    explanation_contents=tuple(
                                        candidate.applied_explanations
                                    )
                                ),
                            )
                            for candidate in section.section_candidates
                        ),
                        explanation=Explanation(
                            explanation_string=f"This is a set of recommended recipes to eat for this day, "
                            f"based on suggesting recipes that you are likely to like in general."
                        ),
                    )
                    for section in soln.solution_section_sets[0].sections
                ),
            ),
        )

        # yield soln

        # yield MealPlanCandidate(
        #     domain_object=MealPlanDay(
        #         recipe_recommendations=tuple(
        #             RecipeRecommendation(
        #                 recipe=candidate.domain_object,
        #                 explanation=RecipeRecommendationExplanation(
        #                     explanation_contents=tuple(candidate.applied_explanations)
        #                 ),
        #             )
        #             for candidate in soln.items
        #         ),
        #         explanation=Explanation(
        #             explanation_string="placeholder hardcoded explanation for a meal plan generation"
        #         ),
        #     ),
        #     context=context,
        #     applied_scores=[soln.overall_score],
        #     applied_explanations=[self.generator_explanation],
        # )
