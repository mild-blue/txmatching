from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import UploadedFileModel


def save_uploaded_file(file: bytes, file_name: str, txm_event_db_id: int, user_id: int):
    uploaded_file_model = UploadedFileModel(
        file=file,
        file_name=file_name,
        txm_event_id=txm_event_db_id,
        user_id=user_id
    )

    db.session.add(uploaded_file_model)
    db.session.commit()
