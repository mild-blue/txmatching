from txmatching.database.services.patient_service import save_patients
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.web import create_app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        patients = parse_excel_data("data.xlsx")
        save_patients(patients)
