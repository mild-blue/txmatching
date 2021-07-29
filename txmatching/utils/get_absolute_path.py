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

    dir_path = os.path.dirname(os.path.realpath(__file__))
    project_root = os.path.abspath(os.path.join(dir_path, '../..'))

    if project_root.endswith('/'):
        project_root = project_root[:-1]

    return project_root + project_relative_path
