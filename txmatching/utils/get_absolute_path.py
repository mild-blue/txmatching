import logging
import os

logger = logging.getLogger(__name__)


def get_absolute_path(project_relative_path: str) -> str:
    """
    Gets absolute path from project relative path
    :param project_relative_path: e.g. "/txmatching/config/configuration.py"
    :return:
    """
    # sanitize input
    if project_relative_path.endswith('/'):
        project_relative_path = project_relative_path[:-1]

    python_path = os.environ['PYTHONPATH'].split(':')
    # case when running from Pycharm
    explicit_paths = [path for path in python_path if path.endswith('txmatching')]
    # use the top level path
    explicit_paths = sorted(explicit_paths, key=len)

    if len(explicit_paths) == 1:
        project_root = explicit_paths[0]
    elif len(python_path) == 1:
        project_root = python_path[0]
    else:
        logger.error(f'Could not determine correct path! PYTHONPATH={python_path}')
        raise AssertionError('It was not possible to determine correct path to resources!')

    # make the path absolute
    project_root = os.path.abspath(project_root)
    if project_root.endswith('/'):
        project_root = project_root[:-1]

    return project_root + project_relative_path
