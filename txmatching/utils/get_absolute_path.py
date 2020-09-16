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
    if not project_relative_path.startswith('/'):
        project_relative_path = f'/{project_relative_path}'

    python_path = os.environ.get('PYTHONPATH')
    if python_path is None:
        python_path = ["."]
    else:
        python_path = python_path.split(':')
    # case when running from Pycharm
    explicit_paths = [path for path in python_path if path.endswith('txmatching')]
    # use the top level path
    explicit_paths = sorted(explicit_paths, key=len)

    # case path set by Pycharm, repo cloned as "txmatching"
    if len(explicit_paths) == 1:
        project_root = explicit_paths[0]
    # case running from command line
    elif len(python_path) == 1:
        project_root = python_path[0]
    # case when we are not sure about the path, so we're guessing,
    # probably running in Pycharm and cloned with different name than "txmatching"
    # then the real directory is usually the first record in the path
    else:
        logger.warning(f'Could not determine correct path! PYTHONPATH={python_path}, using the first.')
        project_root = python_path[0]

    # make the path absolute
    project_root = os.path.abspath(project_root)
    if project_root.endswith('/'):
        project_root = project_root[:-1]

    return project_root + project_relative_path
