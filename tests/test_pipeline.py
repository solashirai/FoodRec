import pytest
from food_rec.models import *
from food_rec.services.food import RecipeEmbeddingService, FoodKgQueryService
from food_rec.services.guideline import GuidelineKgQueryService
from food_rec.services import GraphExplainableFoodRecommenderService
from food_rec.pipeline import *
from food_rec.pipeline_stages import *
from frex.models import Explanation
from frex.models.constraints import ConstraintSolution


def recipe_candidate_placeholder(recipe: FoodKgRecipe, context):
    return RecipeCandidate(
        context=context,
        domain_object=recipe,
        applied_scores=[],
        applied_explanations=[],
    )


def guideline_candidate_placeholder(guideline: Guideline, context):
    return GuidelineCandidate(
        context=context,
        domain_object=guideline,
        applied_scores=[],
        applied_explanations=[],
    )


# @pytest.mark.skip("long skip")
def test_generate_similar_recipes(
    food_kg: FoodKgQueryService,
    embedding_service: RecipeEmbeddingService,
    test_user: FoodKgUser,
):
    user_context = PatientContext(target_user=test_user)
    res = list(
        SimilarToFavoritesRecipeCandidateGenerator(
            recipe_embedding_service=embedding_service, food_kg_query_service=food_kg
        )(context=user_context)
    )

    assert len(res) == 4


def test_prohibited_ingredient_filter(
    food_kg: FoodKgQueryService, test_user: FoodKgUser, test_ingredient_vars
):
    user_context = PatientContext(target_user=test_user)
    filter_stage = ContainsAnyProhibitedIngredientFilter(
        filter_explanation=Explanation(explanation_string="test1")
    )

    og_rec = food_kg.get_recipe_by_uri(
        recipe_uri=test_ingredient_vars.onion_garlic_pot_recipe_uri
    )
    gp_rec = food_kg.get_recipe_by_uri(
        recipe_uri=test_ingredient_vars.gratin_potato_recipe_uri
    )

    og_filter = filter_stage.filter(
        candidate=recipe_candidate_placeholder(og_rec, context=user_context)
    )
    gp_filter = filter_stage.filter(
        candidate=recipe_candidate_placeholder(gp_rec, context=user_context)
    )

    assert og_filter and not gp_filter


def test_calories_below_target_scorer(
    food_kg: FoodKgQueryService, test_user: FoodKgUser, test_ingredient_vars
):
    user_context = PatientContext(target_user=test_user)
    scorer_stage = CaloriesBelowTargetScorer(
        success_scoring_explanation=Explanation(explanation_string="yes test2"),
        failure_scoring_explanation=Explanation(explanation_string="no test2"),
    )

    as_rec = food_kg.get_recipe_by_uri(
        recipe_uri=test_ingredient_vars.amish_soup_recipe_uri
    )
    gp_rec = food_kg.get_recipe_by_uri(
        recipe_uri=test_ingredient_vars.gratin_potato_recipe_uri
    )

    as_score = scorer_stage.score(
        candidate=recipe_candidate_placeholder(as_rec, context=user_context)
    )
    gp_score = scorer_stage.score(
        candidate=recipe_candidate_placeholder(gp_rec, context=user_context)
    )

    assert gp_score == (True, 1) and as_score == (False, 0)


def test_sodium_below_target_scorer(
    food_kg: FoodKgQueryService, test_user: FoodKgUser, test_ingredient_vars
):
    user_context = PatientContext(target_user=test_user)
    scorer_stage = SodiumBelowTargetScorer(
        success_scoring_explanation=Explanation(explanation_string="yes test3"),
        failure_scoring_explanation=Explanation(explanation_string="no test3"),
    )

    as_rec = food_kg.get_recipe_by_uri(
        recipe_uri=test_ingredient_vars.amish_soup_recipe_uri
    )
    gp_rec = food_kg.get_recipe_by_uri(
        recipe_uri=test_ingredient_vars.gratin_potato_recipe_uri
    )

    as_score = scorer_stage.score(
        candidate=recipe_candidate_placeholder(as_rec, context=user_context)
    )
    gp_score = scorer_stage.score(
        candidate=recipe_candidate_placeholder(gp_rec, context=user_context)
    )

    assert gp_score == (True, 1) and as_score == (False, 0)


def test_calorie_scorer(
    food_kg: FoodKgQueryService, test_user: FoodKgUser, test_ingredient_vars
):
    user_context = PatientContext(target_user=test_user)
    scorer_stage = RecipeCaloriesScorer(
        scoring_explanation=Explanation(explanation_string="test4"),
    )

    gp_rec = food_kg.get_recipe_by_uri(
        recipe_uri=test_ingredient_vars.gratin_potato_recipe_uri
    )

    gp_score = scorer_stage.score(
        candidate=recipe_candidate_placeholder(gp_rec, context=user_context)
    )

    assert gp_score == 0.49534


# @pytest.mark.skip("long skip")
def test_rank_recommend_recipes_pipeline(
    food_kg: FoodKgQueryService,
    embedding_service: RecipeEmbeddingService,
    guideline_kg: GuidelineKgQueryService,
    test_user: FoodKgUser,
    test_ingredient_vars,
):

    test_pipe = RecommendRecipesPipeline(
        recipe_embedding_service=embedding_service,
        food_kg=food_kg,
        guideline_kg=guideline_kg,
    )

    res = list(test_pipe(context=PatientContext(target_user=test_user)))

    ld_rec = food_kg.get_recipe_by_uri(
        recipe_uri=test_ingredient_vars.layer_din_recipe_uri
    )
    as_rec = food_kg.get_recipe_by_uri(
        recipe_uri=test_ingredient_vars.amish_soup_recipe_uri
    )
    lg_rec = food_kg.get_recipe_by_uri(
        recipe_uri=test_ingredient_vars.lamb_gratin_recipe_uri
    )
    og_rec = food_kg.get_recipe_by_uri(
        recipe_uri=test_ingredient_vars.onion_garlic_pot_recipe_uri
    )
    gp_rec = food_kg.get_recipe_by_uri(
        recipe_uri=test_ingredient_vars.gratin_potato_recipe_uri
    )

    expected_res = [
        RecipeCandidate(
            context=PatientContext(target_user=test_user),
            domain_object=gp_rec,
            applied_explanations=[
                Explanation(
                    explanation_string="This recipe had a similarity score of 0.012105363142076218 "
                    "to one of your favorite recipes, Lamb Chops au Gratin."
                ),
                Explanation(
                    explanation_string="This recipe does not contain any ingredients that are prohibited by you."
                ),
                Explanation(
                    explanation_string="Adheres to guideline: As for the general population, people with diabetes should limit sodium consumption to <2,300 mg/day."
                ),
                Explanation(
                    explanation_string="Scoring based on calories, this is mostly a placeholder to break ties."
                ),
            ],
            applied_scores=[0.012105363142076218, 0, 1, 0.49534],
        ),
        RecipeCandidate(
            context=PatientContext(target_user=test_user),
            domain_object=as_rec,
            applied_explanations=[
                Explanation(
                    explanation_string="This recipe had a similarity score of 1.0 "
                    "to one of your favorite recipes, Lamb Chops au Gratin."
                ),
                Explanation(
                    explanation_string="This recipe does not contain any ingredients that are prohibited by you."
                ),
                Explanation(
                    explanation_string="Does not adhere to guideline: As for the general population, people with diabetes should limit sodium consumption to <2,300 mg/day."
                ),
                Explanation(
                    explanation_string="Scoring based on calories, this is mostly a placeholder to break ties."
                ),
            ],
            applied_scores=[1.0, 0, 0, -1.9261110339999998],
        ),
        RecipeCandidate(
            context=PatientContext(target_user=test_user),
            domain_object=ld_rec,
            applied_explanations=[
                Explanation(
                    explanation_string="This recipe had a similarity score of 1.0 "
                    "to one of your favorite recipes, Lamb Chops au Gratin."
                ),
                Explanation(
                    explanation_string="This recipe does not contain any ingredients that are prohibited by you."
                ),
                Explanation(
                    explanation_string="Does not adhere to guideline: As for the general population, people with diabetes should limit sodium consumption to <2,300 mg/day."
                ),
                Explanation(
                    explanation_string="Scoring based on calories, this is mostly a placeholder to break ties."
                ),
            ],
            applied_scores=[1.0, 0, 0, -1.9750581350000003],
        ),
    ]

    assert res == expected_res


def test_generate_guidelines(test_user, guideline_kg):
    user_context = PatientContext(target_user=test_user)
    res = AllGuidelinesCandidateGenerator(guideline_query_service=guideline_kg)(
        context=user_context
    )

    assert len(list(res)) == 3


def test_filter_applicable_guidelines(
    test_user, placeholder_guideline, placeholder_guideline2
):
    user_context = PatientContext(target_user=test_user)
    candidates = [
        guideline_candidate_placeholder(placeholder_guideline, context=user_context),
        guideline_candidate_placeholder(placeholder_guideline2, context=user_context),
    ]
    res = list(
        UserMatchGuidelineFilter(filter_explanation=Explanation("test1"))(
            candidates=candidates, context=user_context
        )
    )
    assert res == [
        GuidelineCandidate(
            context=user_context,
            domain_object=placeholder_guideline,
            applied_explanations=[Explanation(explanation_string="test1")],
            applied_scores=[0],
        )
    ]


def test_generate_guideline_pipeline(test_user, guideline_kg, placeholder_guideline):
    pipe = GenerateGuidelinesApplicableToUserPipeline(guideline_kg=guideline_kg)
    res = list(pipe(context=PatientContext(target_user=test_user)))

    assert res == [
        GuidelineCandidate(
            context=PatientContext(target_user=test_user),
            domain_object=placeholder_guideline,
            applied_explanations=[
                Explanation(
                    explanation_string="This is a guideline that exists in the system."
                ),
                Explanation(
                    explanation_string="User matches the conditions to apply this guideline."
                ),
            ],
            applied_scores=[0, 0],
        )
    ]


def test_mealplan_pipeline(
    test_user_2,
    food_kg: FoodKgQueryService,
    embedding_service: RecipeEmbeddingService,
    guideline_kg: GuidelineKgQueryService,
):

    test_pipe = RecommendMealPlanPipeline(
        recipe_embedding_service=embedding_service,
        food_kg=food_kg,
        guideline_kg=guideline_kg,
        number_of_days=2,
        meals_per_day=2,
    )

    # currently only produces 1 output
    res = list(test_pipe(context=PatientContext(target_user=test_user_2)))[0]

    assert (
        res.context
        == PatientContext(target_user=test_user_2)
        # and isinstance(res.domain_object, ConstraintSolution)
        # and len(res.domain_object.items) == 4
        # and len(res.domain_object.solution_section_sets) == 1
        # and len(res.domain_object.solution_section_sets[0].sections) == 2
        # and len(res.domain_object.solution_section_sets[0].sections[0].section_candidates) == 2
    )
