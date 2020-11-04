import unittest

import yaml

from tests.test_utilities.generate_swagger import (PATH_TO_SWAGGER_YAML,
                                                   SwaggerGenApp)


class TestMatchingApi(unittest.TestCase):

    def test_swagger_generation(self):
        app_for_swagger_gen = SwaggerGenApp()
        with open(PATH_TO_SWAGGER_YAML) as f:
            self.maxDiff = None
            old_swagger = yaml.load(f)
        new_swagger = app_for_swagger_gen.api.__schema__
        # can be used if one wantes to compare what is the issue
        # with open(get_absolute_path("tests/resources/test_swagger_new.json"), "w") as f:
        #     json.dump(new_swagger, f, ensure_ascii=False, indent=4)
        self.assertDictEqual(old_swagger, new_swagger)
