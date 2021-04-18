from urllib.parse import quote
import json

import pytest

from flask_app.main import create_app


def format_res_for_test(res):
    res_json = json.loads(res.data)
    return set(
        (opt["fromIngredient"], opt["toIngredient"], opt["explanation"])
        for opt in res_json["substitution_options"]
    )


@pytest.fixture
def client():
    app = create_app(TESTING=True)

    with app.test_client() as client:
        yield client


def test_get_recipe_subs(client, food_kg, test_ingredient_vars):
    res = client.get(
        f"/recipe_subs?recipe_uri={quote(test_ingredient_vars.gratin_potato_recipe_uri)}"
    )
    res_formatted = format_res_for_test(res)

    expected_res = set(
        (
            str(test_ingredient_vars.potato_uri),
            str(uri),
            "fake explanation hardcoded sub",
        )  # from, to, expl
        for uri in test_ingredient_vars.potato_subs_uris
    )

    assert res_formatted == expected_res


def test_get_recipe_user_subs(client, food_kg, test_ingredient_vars, test_user_vars):
    res = client.get(
        f"/recipe_user_subs?recipe_uri={quote(test_ingredient_vars.layer_din_recipe_uri)}&user_uri={quote(test_user_vars.user_uri)}"
    )
    res_formatted = format_res_for_test(res)

    expected_res = set(
        (
            str(test_ingredient_vars.carrot_uri),
            str(uri),
            "fake explanation hardcoded sub",
        )  # from, to, expl
        for uri in test_ingredient_vars.low_carb_carrot_subs
    )
    expected_res = expected_res.union(
        (
            str(test_ingredient_vars.potato_uri),
            str(uri),
            "fake explanation hardcoded sub",
        )  # from, to, expl
        for uri in test_ingredient_vars.potato_subs_uris
    )

    assert res_formatted == expected_res
