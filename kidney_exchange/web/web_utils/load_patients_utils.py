from flask import current_app as app


def is_allowed_file_extension(filename):
    ext = filename.split(".")[1]
    if ext.upper() in app.config["ALLOWED_FILE_EXTENSIONS"]:
        return True
    else:
        return False
