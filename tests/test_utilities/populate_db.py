from txmatching.auth.data_types import UserRole
from txmatching.database.services.app_user_management import persist_user
from txmatching.database.services.patient_service import overwrite_patients_by_patients_from_excel
from txmatching.database.sql_alchemy_schema import AppUserModel, ConfigModel
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.web import create_app
from txmatching.auth.crypto import encode_password

ADMIN_USER = {
    'id': 1,
    'email': 'admin@example.com',
    'password': 'admin'
}


def add_users():
    ConfigModel.query.delete()
    AppUserModel.query.delete()
    app_user = AppUserModel(
        email=ADMIN_USER['email'],
        pass_hash=encode_password(ADMIN_USER['password']),
        role=UserRole.ADMIN)
    persist_user(app_user)
    ADMIN_USER['id'] = app_user.id
    assert len(AppUserModel.query.all()) == 1


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        patients = parse_excel_data('data.xlsx')
        overwrite_patients_by_patients_from_excel(patients)
        add_users()
