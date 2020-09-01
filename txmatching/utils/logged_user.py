from flask import g


def get_current_user_id() -> int:
    """
    Retrieves user id from the request context.

    Can trow AttributeError if not executed inside the Flask context.
    """
    return g.user_id
