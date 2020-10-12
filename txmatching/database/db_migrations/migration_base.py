import os

from alembic import op
from sqlalchemy import text


def execute(filename: str):
    """
    Helper function for RAW SQL execution.
    :param filename:
    :return:
    """
    directory = os.path.dirname(os.path.realpath(__file__))
    conn = op.get_bind()
    path = os.path.join(directory, 'versions', filename)
    with open(path) as file:
        script = file.read()
        conn.execute(text(script))
