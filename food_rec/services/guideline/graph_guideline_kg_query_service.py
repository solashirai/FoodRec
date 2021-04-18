from food_rec.utils import cfg
from food_rec.models import *
from food_rec.services.graph import _GraphQueryService
from food_rec.services.guideline import GuidelineKgQueryService
from rdflib import URIRef, Graph
from frex.models import Explanation, ConstraintType
from typing import Optional, Tuple


class GraphGuidelineKgQueryService(_GraphQueryService, GuidelineKgQueryService):
    def __init__(self, **kwargs):
        self.temp_guideline_uri_dict = dict()

        # Currently using example hard-coded guidelines
        self.temp_guideline_uri_dict[URIRef("exampleGuideline1")] = Guideline(
            uri=URIRef("exampleGuideline1"),
            user_conditions=frozenset(),
            filter_directives=frozenset(),
            scoring_directives=frozenset(
                {
                    GuidelineDirective(
                        target_value=2300,
                        target_attribute="total_nutritional_info.sodium_mg",
                        directive_type=ConstraintType.LEQ,
                    )
                }
            ),
            explanation=Explanation(
                explanation_string="As for the general population, people with diabetes should limit sodium consumption to <2,300 mg/day."
            ),
        )

        self.temp_guideline_uri_dict[URIRef("exampleGuideline2")] = Guideline(
            uri=URIRef("exampleGuideline2"),
            user_conditions=frozenset(
                {
                    lambda usr: usr.sex == "male",
                    lambda usr: usr.bmi is not None and usr.bmi > 0,
                }
            ),
            filter_directives=frozenset(),
            scoring_directives=frozenset(
                {
                    GuidelineDirective(
                        target_value=1800,
                        target_attribute="total_nutritional_info.energ__kcal",
                        directive_type=ConstraintType.LEQ,
                    )
                }
            ),
            explanation=Explanation(
                explanation_string="1,500–1,800 kcal/day for men, adjusted for the individuals baseline body weight"
            ),
        )

        self.temp_guideline_uri_dict[URIRef("exampleGuideline3")] = Guideline(
            uri=URIRef("exampleGuideline3"),
            user_conditions=frozenset(
                {
                    lambda usr: all(
                        val in usr.target_lifestyle_guideline_set
                        for val in frozenset(
                            {
                                URIRef(
                                    "http://idea.rpi.edu/heals/kb/placeholder/fakeuri3"
                                )
                            }
                        )
                    )
                }
            ),
            filter_directives=frozenset(),
            scoring_directives=frozenset(),
            explanation=Explanation(
                explanation_string="mediterranean diet. prefer including subclasses of fruit, nuts, fish, vegetable, legume, olive oil, dairy. only based on links existing in recipes-1. this placeholder is not a great example of a real guideline."
            ),
        )
        super().__init__(**kwargs)

    def get_all_guidelines(self) -> Tuple[Guideline]:
        """
        Retrieve all guidelines present in the guideline KG. Currently all guidelines are hardcoded placeholders.
        :return: A tuple of all Guideline objects that are present in the current guideline KG.
        """
        return tuple([g for g in self.temp_guideline_uri_dict.values()])

    def get_guideline_by_uri(self, *, guideline_uri: URIRef) -> Guideline:
        """
        Query the guideline KG to retrieve a guideline by its URI.

        :param guideline_uri: the URI of the target guideline
        :return: a Guidline object with the target URI
        """
        # placeholder result graph, since we are not using a real guideline KG yet
        guideline = self._graph_get_guideline_by_uri(guideline_uri=guideline_uri)

        return guideline

    def get_guidelines_by_conditions(
        self,
        *,
        age: Optional[int] = None,
        bmi: Optional[float] = None,
        sex: Optional[str] = None
    ) -> Tuple[Guideline]:
        """
        Retrieve guidelines that apply to patients with specific input parameters.

        :param age: the patient age to compare against guideline conditions
        :param bmi: the patient bmi to compare against guideline conditions
        :param sex: the patient sex to compare against guideline conditions
        :return: Guideline objects whose conditions are fulfilled by te input parameters
        """
        # create a fake user based on the input conditions and use it to filter which guidelines are applicable
        fake_user_profile = FoodKgUser(
            sex=sex,
            age=age,
            bmi=bmi,
            name="",
            uri=None,
            favorite_recipe_uri_set=frozenset(),
            prohibited_ingredient_uri_set=frozenset(),
            prohibited_foodon_class_set=frozenset(),
            available_ingredient_uri_set=frozenset(),
            target_lifestyle_guideline_set=frozenset(),
            nutrition_constraint_set=frozenset(),
        )

        all_guidelines = self.get_all_guidelines()
        guidelines = [
            g
            for g in all_guidelines
            if all(c(fake_user_profile) for c in g.user_conditions)
        ]

        return tuple(guidelines)

    def _graph_get_guideline_by_uri(self, *, guideline_uri: URIRef) -> Guideline:
        """
        Retrieve a guideline from the graph with the given URI.

        :param guideline_uri: the URI of the guideline to retrieve
        :return: a Guideline object
        """

        # currently just using a static dictionary of example guidelines
        return self.temp_guideline_uri_dict.get(
            guideline_uri,
            Guideline(
                uri=guideline_uri,
                user_conditions=frozenset({}),
                filter_directives=frozenset(),
                scoring_directives=frozenset(),
                explanation=Explanation(explanation_string=""),
            ),
        )
