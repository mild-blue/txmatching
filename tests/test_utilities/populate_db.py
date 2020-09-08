from txmatching.database.services.app_user_management import persist_user
from txmatching.database.services.patient_service import save_all_patients_from_excel
from txmatching.database.sql_alchemy_schema import AppUser
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.web import create_app
from txmatching.web.auth.crypto import encode_password

ADMIN_USER = {
    'id': 1,
    'email': 'admin@example.com',
    'password': 'admin'
}


def add_users():
    app_user = AppUser(
        email=ADMIN_USER['email'],
        pass_hash=encode_password(ADMIN_USER['password']),
        role='ADMIN')
    persist_user(app_user)
    ADMIN_USER['id'] = app_user.id
    assert AppUser.query.get(1) is not None


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        patients = parse_excel_data('data.xlsx')
        save_all_patients_from_excel(patients)
        add_users()
