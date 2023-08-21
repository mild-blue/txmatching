import inspect
import logging
from dataclasses import dataclass
from types import FrameType, TracebackType
from typing import Dict, List, Optional, Type

logger = logging.getLogger(__name__)


@dataclass
class ExceptionInfo:
    """Corresponds to the return value from sys.exc_info()."""
    type_exception: Type[BaseException]
    exception: BaseException
    traceback: Optional[TracebackType]


@dataclass
class TracebackFramesParsingResult:
    frames: List[FrameType]
    have_all_frames_been_parsed: bool


def exc_info_to_dict(exc_info: ExceptionInfo):
    """
    Transform exc_info from sys.exc_info() to dict.
    :param exc_info: exc_info with type ExceptionInfo.
    :return:
        Dict{
            error: error class,
            error_message: message provided with error,
            traceback: list of frames in dict format
          * traceback_parsing_warning: shown if there is a warning about the huge amount of trace frames
        }
    * - optional output
    """
    tb_frames_parsing_result = _get_traceback_frames(exc_info.traceback) if \
            exc_info.traceback else TracebackFramesParsingResult(frames=[],
                                                                 have_all_frames_been_parsed=True)

    traceback = list(map(_frame_to_dict, tb_frames_parsing_result.frames))
    exc_info_dict = {
            'error': exc_info.type_exception.__name__,
            'error_message': str(exc_info.exception),
            'traceback': traceback
    }
    if not tb_frames_parsing_result.have_all_frames_been_parsed:
        exc_info_dict |= {'traceback_parsing_warning': 'There are too many frames in the traceback object. '
                                                       'You only see the first ones available. '
                                                       'The rest are not displayed in the logs'}

    return exc_info_dict


def _get_traceback_frames(traceback: TracebackType, max_frames_amount=100) -> \
        TracebackFramesParsingResult:
    """
    Gets all frames from traceback.
    :param traceback: traceback with type TracebackType.
    :param max_frames_amount: max amount of frames in the traceback.
    :return: dataclass TracebackFramesParsingResult that includes list of frames and
             information about if all traceback frames have been parsed.
    """
    frames: List[FrameType] = []
    while traceback is not None:
        frames.append(traceback.tb_frame)
        traceback = traceback.tb_next
        if len(frames) >= max_frames_amount:
            return TracebackFramesParsingResult(frames=frames,
                                                have_all_frames_been_parsed=False)
    return TracebackFramesParsingResult(frames=frames,
                                        have_all_frames_been_parsed=True)


def _frame_to_dict(frame: FrameType) -> Dict[str, str]:
    """
    Transform frame with type FrameType to dict.
    P.S. Transfer from frame info only filename, lineno, function, code_context attributes!
    :param frame: frame with type FrameType
    :return:
        Dict{
            'filename': corresponds to inspect.FrameInfo.filename,
            'lineno': corresponds to inspect.FrameInfo.lineno,
            'function': corresponds to inspect.FrameInfo.function,
            'code_context': corresponds to inspect.FrameInfo.code_context
        }
    """
    frame_info = inspect.getframeinfo(frame)
    return {
        'filename': frame_info.filename,
        'lineno': frame_info.lineno,
        'function': frame_info.function,
        'code_context': [ctx_line.strip().replace('\n', '')
                         for ctx_line in frame_info.code_context]
    }
