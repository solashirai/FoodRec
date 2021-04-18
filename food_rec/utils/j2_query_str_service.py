import jinja2 as j2

from food_rec.utils.path import SPARQL_J2_DIR
from food_rec.utils import cfg


class J2QueryStrService:

    TEMPLATE_ENV = j2.Environment(loader=j2.FileSystemLoader(SPARQL_J2_DIR))

    @staticmethod
    def j2_query(*, file_name, **kwargs) -> str:
        """
        Return a j2 query template with the given file name, populated with the given arguments.

        :param file_name: the name of the j2 template, not including any suffix
        :param kwargs: any parameters to fill in the template
        :return: a string result of rendering the j2 template with the arguments present in kwargs
        """
        query_template = J2QueryStrService.TEMPLATE_ENV.get_template(
            file_name + ".sparql.j2"
        )
        query_str = query_template.render(**kwargs)

        return query_str
