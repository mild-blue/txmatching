import os
import re
from typing import List, Tuple

import pandas as pd

from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.patient_parameters import PatientParameters
from kidney_exchange.patients.recipient import Recipient

_valid_blood_groups = ["A", "B", "0", "AB"]

_valid_allele_codes = ["A1", "A2", "A203", "A210", "A3", "A11", "A23", "A24", "A2403",
                       "A25", "A26", "A29", "A30", "A31", "A32", "A33", "A34", "A36", 
                       "A43", "A66", "A68", "A69", "A74", "A80", "B7", "B703", "B8", 
                       "B13", "B18", "B27", "B2708", "B35", "B37","B38", "B39", "B3901",
                       "B3902", "B4005", "B41", "B42", "B44","B45", "B46", "B47", "B48",
                       "B49", "B50", "B51", "B5102", "B5103","B52", "B53", "B54", "B55",
                       "B56", "B57", "B58", "B59", "B60","B61", "B62", "B63", "B64", "B65",
                       "B67", "B71", "B72", "B73", "B75", "B76", "B77", "B78", "B81", "B82",
                       "Cw1", "Cw2", "Cw4", "Cw5", "Cw6", "Cw7", "Cw8", "Cw9", "Cw10",
                       "DR1", "DR103", "DR4", "DR7", "DR8", "DR9", "DR10", "DR11", "DR12",
                       "DR13", "DR14", "DR1403", "DR1404", "DR15", "DR16", "DR17", "DR18",
                       "DR51", "DR52", "DR53", "DQ2", "DQ4", "DQ5", "DQ6", "DQ7", "DQ8", "DQ9"]

def _parse_blood_groups(blood_groups_str: str) -> List[str]:
    blood_groups_str = str(blood_groups_str).strip()
    blood_groups = re.split("[, ]+", blood_groups_str)
    checked_blood_groups = [group for group in blood_groups if group in _valid_blood_groups]
    if len(checked_blood_groups) != len(blood_groups):
        print(f"[WARN] Encountered invalid group in blood group string {blood_groups_str}")

    return checked_blood_groups


def _parse_hla(hla_allele_str: str) -> List[str]:
    if "neg" in hla_allele_str.lower():
        return []

    allele_codes = re.split("[, ()]+", hla_allele_str)
    allele_codes = [code for code in allele_codes if len(code) > 0]
    checked_allele_codes = [code for code in allele_codes if code in _valid_allele_codes]
    allele_codes_difference = [code for code in allele_codes if code not in checked_allele_codes]
    if len(checked_allele_codes) != len(allele_codes):
        print(f"[WARN] Encoutered invalid code in allele codes string {hla_allele_str}\n")
        print(f"Following codes are not in the anitgen codes table: \n {', '.join(allele_codes_difference)}")
    return allele_codes


def _country_code_from_id(patient_id: str) -> str:
    # TODO: Confirm this with IKEM
    if patient_id.startswith("P-"):
        return "CZE"

    if patient_id.startswith("I-"):
        return "IL"

    if patient_id.startswith("W-") or patient_id.startswith("IS-") or patient_id.startswith("G-"):
        return "AUT"

    raise ValueError(f"Could not assign country code to {patient_id}")


def parse_excel_data(file_path: str) -> Tuple[List[Donor], List[Recipient]]:
    print(f"[INFO] Parsing patient data from file {file_path}")
    data = pd.read_excel(file_path, skiprows=1)
    donors = list()
    recipients = list()
    for index, row in data.iterrows():
        donor_id = row["DONOR"]
        blood_group_donor = _parse_blood_groups(row["BLOOD GROUP donor"])[0]
        typization_donor = _parse_hla(row["TYPIZATION DONOR"])
        country_code_donor = _country_code_from_id(donor_id)
        donor_params = PatientParameters(blood_group=blood_group_donor,
                                         hla_antigens=typization_donor,
                                         country_code=country_code_donor)
        donor = Donor(patient_id=donor_id, parameters=donor_params)
        donors.append(donor)

        recipient_id = row["RECIPIENT"]
        if not pd.isna(recipient_id):
            blood_group_recipient = _parse_blood_groups(row["BLOOD GROUP recipient"])[0]
            typization_recipient = _parse_hla(row["TYPIZATION RECIPIENT"])
            antibodies_recipient = _parse_hla(row["luminex  cut-off (2000 MFI) varianta 2"])
            acceptable_blood_groups_recipient = _parse_blood_groups(row["Acceptable blood group"])
            country_code_recipient = _country_code_from_id(recipient_id)

            recipient_params = PatientParameters(blood_group=blood_group_recipient,
                                                 hla_antigens=typization_recipient,
                                                 hla_antibodies=antibodies_recipient,
                                                 acceptable_blood_groups=acceptable_blood_groups_recipient,
                                                 country_code=country_code_recipient)
            recipient = Recipient(patient_id=recipient_id, parameters=recipient_params, related_donors=donor)
            recipients.append(recipient)

    return donors, recipients


if __name__ == "__main__":
    patient_data_path = os.getenv("PATIENT_DATA_PATH")
    final_donors, final_recipients = parse_excel_data(patient_data_path)
    print("\nDonors: \n" + "-" * 50 + "\n")
    for final_donor in final_donors:
        print(final_donor)

    print("\nRecipients: \n" + "-" * 50 + "\n")
    for final_recipient in final_recipients:
        print(final_recipient)
