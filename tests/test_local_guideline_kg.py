from food_rec.services.guideline import GraphGuidelineKgQueryService
from food_rec.models import *
from food_rec.utils import cfg


def test_get_guideline_by_uri(
    guideline_kg: GraphGuidelineKgQueryService, placeholder_guideline, test_user
):
    guideline = guideline_kg.get_guideline_by_uri(
        guideline_uri=cfg.HARDCODED_GUIDELINE_URI_1
    )

    assert guideline == placeholder_guideline


def test_get_guidelines_by_conditions(
    guideline_kg: GraphGuidelineKgQueryService,
    placeholder_guideline_comp,
    placeholder_guideline2_comp,
    test_user_2: FoodKgUser,
):
    guidelines = guideline_kg.get_guidelines_by_conditions(
        age=test_user_2.age, bmi=test_user_2.bmi, sex=test_user_2.sex
    )

    assert set(guidelines) == {placeholder_guideline_comp, placeholder_guideline2_comp}
