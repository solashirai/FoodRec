from food_rec.services.user import LocalGraphUserKgQueryService
from food_rec.services.exceptions import *
from rdflib import URIRef
import pytest


def test_raise_exceptions(user_kg: LocalGraphUserKgQueryService):
    with pytest.raises(UserNotFoundException):
        user_kg.get_user_by_uri(user_uri=URIRef("bad_user"))


def test_get_user_by_uri(
    user_kg: LocalGraphUserKgQueryService, test_user, test_user_vars
):
    usr = user_kg.get_user_by_uri(user_uri=test_user_vars.user_uri)

    expected_usr = test_user

    assert expected_usr == usr


def test_get_user_by_uri_with_less_details(
    user_kg: LocalGraphUserKgQueryService, test_user_2, test_user_vars
):
    usr = user_kg.get_user_by_uri(user_uri=test_user_vars.user_uri_2)

    expected_usr = test_user_2

    assert expected_usr == usr
