import inspect
import sys
import traceback
import unittest
from pathlib import Path

from txmatching.web.web_utils.traceback_formatters import (
    ExceptionInfo, _frame_to_dict, _get_traceback_frames, exc_info_to_dict)


class TestExcInfoToDict(unittest.TestCase):

    def test_exc_info_to_dict(self):
        try:
            raise ValueError('general case')
        except ValueError:
            exc_info = sys.exc_info()
            result = exc_info_to_dict(ExceptionInfo(exc_info[0],
                                                    exc_info[1],
                                                    exc_info[2]))
            self.assertEqual(result, {
                'error': 'ValueError',
                'error_message': 'general case',
                'traceback': [{
                    'filename': str(Path(__file__).absolute()),
                    'function': 'test_exc_info_to_dict',
                    'lineno': 18,
                    'code_context': ['result = exc_info_to_dict(ExceptionInfo(exc_info[0],']
                }]
            })

    def test_exc_info_to_dict_without_traceback(self):
        try:
            raise ValueError('without traceback')
        except ValueError:
            exc_info = sys.exc_info()
            result = exc_info_to_dict(ExceptionInfo(exc_info[0],
                                                    exc_info[1],
                                                    None))
            self.assertEqual(result, {
                'error': 'ValueError',
                'error_message': 'without traceback',
                'traceback': []
            })


class TestGetTracebackFrames(unittest.TestCase):

    def test_get_traceback_frames(self):
        try:
            def inner_raise():
                raise ValueError('general case')

            inner_raise()
        except ValueError:
            exc_info = sys.exc_info()
            tb = exc_info[2]
            self.assertTrue(_get_traceback_frames(tb).have_all_frames_been_parsed)
            frames = _get_traceback_frames(tb).frames
            self.assertEqual(len(frames), 2)
            self.assertEqual(frames[0].f_lineno, 61)
            self.assertEqual(frames[1].f_lineno, 52)

    def test_get_traceback_frames_with_max_frames_amount(self):
        try:
            def inner_raise(n):
                if n == 0:
                    raise ValueError('error message')
                inner_raise(n - 1)

            inner_raise(200)
        except ValueError:
            exc_info = sys.exc_info()
            tb = exc_info[2]
            tb_frames_parsing_result = _get_traceback_frames(tb, max_frames_amount=101)
            self.assertFalse(tb_frames_parsing_result.have_all_frames_been_parsed)
            self.assertEqual(len(tb_frames_parsing_result.frames), 101)


class TestFrameToDict(unittest.TestCase):

    def test_frame_to_dict(self):
        frame = inspect.currentframe()
        frame_dict = _frame_to_dict(frame)

        self.assertEqual(frame_dict.get('filename'), __file__)
        self.assertEqual(frame_dict.get('lineno'), 84)
        self.assertEqual(frame_dict.get('function'), 'test_frame_to_dict')
        self.assertEqual(frame_dict.get('code_context')[0], 'frame_dict = _frame_to_dict(frame)')
