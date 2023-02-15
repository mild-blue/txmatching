import inspect
import logging

from dataclasses import dataclass
from types import TracebackType, FrameType
from typing import Dict, List, Optional, Type

logger = logging.getLogger(__name__)


@dataclass
class ExcInfo:
    """Corresponds to the return value from sys.exc_info()."""
    type_exception: Type[BaseException]
    exception: BaseException
    traceback: Optional[TracebackType]


def exc_info_to_dict(exc_info: ExcInfo):
    """
    Transform exc_info from sys.exc_info() to dict.
    :param exc_info: exc_info with type ExcInfo.
    :return:
        Dict{
            error: error class,
            error_message: message provided with error,
            traceback: list of frames in dict format
        }
    """
    traceback = list(map(_frame_to_dict, _get_traceback_frames(exc_info.traceback))) if \
                    exc_info.traceback else []
    return {
        'error': exc_info.type_exception.__name__,
        'error_message': str(exc_info.exception),
        'traceback': traceback
    }


def _get_traceback_frames(traceback: TracebackType, max_frames_amount=100) -> List[FrameType]:
    """
    Gets all frames from traceback.
    :param traceback: traceback with type TracebackType.
    :param max_frames_amount: max amount of frames in the traceback.
    :return: list of frames with type FrameType or
             raises TimeoutError if frames amount limit is reached to the max_frames_amount value.
    """
    frames: List[FrameType] = []
    while traceback is not None:
        frames.append(traceback.tb_frame)
        traceback = traceback.tb_next
        if len(frames) > max_frames_amount:
            logger.info(f"There are too many frames in the traceback object. "
                        f"(more than {max_frames_amount}). "
                        f"The rest of the frames will not be displayed in the logs.")
            break
    return frames


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
