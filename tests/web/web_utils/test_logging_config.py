import unittest

from txmatching.web.web_utils.logging_config import \
    _hide_sensitive_values_in_request_arguments


class TestHideSensitiveValuesInRequestArguments(unittest.TestCase):

    def test_hide_sensitive_values_in_request_arguments_no_pattern(self):
        """No sensitive data -> no changes (nothing to hide)"""
        arguments = {
            'name': 'James',
            'surname': 'Bond',
            'age': 50
        }

        self.assertEqual(arguments,
                         _hide_sensitive_values_in_request_arguments(arguments))

    def test_hide_sensitive_values_in_request_arguments_no_recursion(self):
        """There is sensitive data, but there aren't dicts inside dict"""
        arguments = {
            'name': 'James',
            'surname': 'Bond',
            'age': 50,
            'mypassword': 'bond007',
            'bondcreatedpasswordbymi6': '007UKbrexit',
            'itisnotpasswor_d': 'i love cats',
            'password': 12345678
        }

        self.assertEqual(_hide_sensitive_values_in_request_arguments(arguments),
                         {
                             'name': 'James',
                             'surname': 'Bond',
                             'age': 50,
                             'mypassword': '*********',
                             'bondcreatedpasswordbymi6': '*********',
                             'itisnotpasswor_d': 'i love cats',
                             'password': '*********'
                         })

    def test_hide_sensitive_values_in_request_arguments_recursion(self):
        """Sensitive data inside dicts in the main dict"""
        arguments = {
            'name': 'James',
            'surname': 'Bond',
            'age': 50,
            'more_info': {
                'more_more_info': {
                    'mypassword': 'bond007',
                    'bondcreatedpasswordbymi6': '007UKbrexit',
                    'itisnotpasswor_d': 'i love cats',
                    'password': 12345678
                }
            }
        }

        self.assertEqual(_hide_sensitive_values_in_request_arguments(arguments),
                         {
                             'name': 'James',
                             'surname': 'Bond',
                             'age': 50,
                             'more_info': {
                                 'more_more_info': {
                                     'mypassword': '*********',
                                     'bondcreatedpasswordbymi6': '*********',
                                     'itisnotpasswor_d': 'i love cats',
                                     'password': '*********'
                                 }
                             }
                         })
