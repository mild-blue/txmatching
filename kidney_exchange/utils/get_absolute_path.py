import os


def get_absolute_path(project_relative_path: str) -> str:
    """
    Gets absolute path from project relative path
    :param project_relative_path: e.g. "/kidney_exchange/config/configuration.py"
    :return:
    """
    path_parts = os.path.abspath(__file__).split("/")
    directory_index = path_parts.index("kidney-exchange")
    project_path = "/".join(path_parts[:(directory_index + 1)])
    if not project_relative_path.startswith("/"):
        project_relative_path = f"/{project_relative_path}"
    absolute_path = project_path + project_relative_path
    return absolute_path


if __name__ == "__main__":
    test_file_path = "/tests/resources/sample_score_matrix.txt"
    abs_path = get_absolute_path(test_file_path)
    print(abs_path)
