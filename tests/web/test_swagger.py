import json
import unittest

from tests.test_utilities.generate_swagger import (PublicSwaggerGenApp,
                                                   SwaggerGenApp)
from txmatching.web import PATH_TO_PUBLIC_SWAGGER_JSON, PATH_TO_SWAGGER_JSON


class TestMatchingApi(unittest.TestCase):

    def test_swagger_generation(self):
        with open(PATH_TO_SWAGGER_JSON) as f:
            self.maxDiff = None
            old_swagger = json.load(f)
        new_swagger = SwaggerGenApp().api.__schema__
        # Can be used if one wants to compare what is the issue.
        # with open(get_absolute_path("tests/resources/test_swagger_new.json"), "w") as f:
        #     swagger_without_ordered_dict = {k: dict(v) if isinstance(v, OrderedDict) else v for k, v in
        #                                     new_swagger.items()}
        #     json.dump(swagger_without_ordered_dict, f, ensure_ascii=False, indent=4)
        self.assertDictEqual(old_swagger, new_swagger, msg='Swagger generated not equal to current '
                                                           'maybe you have simply forgotten to regenerate it in '
                                                           'test_utilities/generate_swagger.py?')

    def test_public_swagger_generation(self):
        with open(PATH_TO_PUBLIC_SWAGGER_JSON) as f:
            self.maxDiff = None
            old_swagger = json.load(f)
        new_swagger = PublicSwaggerGenApp().api.__schema__
        # Can be used if one wants to compare what is the issue.
        # with open(get_absolute_path("tests/resources/test_swagger_new.json"), "w") as f:
        #     swagger_without_ordered_dict = {k: dict(v) if isinstance(v, OrderedDict) else v for k, v in
        #                                     new_swagger.items()}
        #     json.dump(swagger_without_ordered_dict, f, ensure_ascii=False, indent=4)
        self.assertDictEqual(old_swagger, new_swagger, msg='Swagger generated not equal to current '
                                                           'maybe you have simply forgotten to regenerate it in '
                                                           'test_utilities/generate_swagger.py?')
