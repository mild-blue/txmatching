from typing import List, Dict, Tuple, Iterator

from kidney_exchange.config.configuration import Configuration
from kidney_exchange.database.sql_alchemy_schema import ConfigModel, PairingResultModel, PairingResultPatientModel, \
    PatientModel, PatientPairModel
from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.patient import Patient
from kidney_exchange.patients.patient_parameters import PatientParameters
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.solvers.matching.matching import Matching


def get_config_models(order_by=ConfigModel.created_at) -> List[ConfigModel]:
    configs = ConfigModel.query.order_by(order_by).all()
    return configs


def config_model_to_config(config_model: ConfigModel) -> Configuration:
    return Configuration(**config_model.parameters)


def get_configs() -> Iterator[Configuration]:
    for config_model in get_config_models():
        yield config_model_to_config(config_model)


def get_latest_configuration() -> Configuration:
    latest_config_model = get_config_models(order_by=ConfigModel.created_at)[-1]
    return config_model_to_config(latest_config_model)


def get_configs_compatible_with_params(params: Dict) -> List[ConfigModel]:
    configs = get_config_models()
    return [config for config in configs if _compatible(config, params)]


def _compatible(config: ConfigModel, params) -> bool:
    config_object = Configuration(**config.parameters)
    return all([getattr(config_object, key) == value for key, value in params.items()])


def get_pairing_result_for_config(config_id) -> List[PairingResultModel]:
    return PairingResultModel.query.filter(PairingResultModel.config_id == config_id).all()


def get_patients_for_pairing_result(pairing_result_id) -> List[PairingResultPatientModel]:
    return PairingResultPatientModel.query.filter(
        PairingResultPatientModel.pairing_result_id == pairing_result_id).all()


def db_matching_to_matching(json_matchings: List[List[Dict[str, int]]]) -> List[Matching]:
    return [Matching([get_patients_from_ids(tup['donor'], tup['recipient'])
                      for tup in json_matching
                      ]) for json_matching in json_matchings]


def get_patients_from_ids(donor_id, recipient_id) -> Tuple[Donor, Recipient]:
    return get_donor_from_db(donor_id), get_recipient_from_db(recipient_id)


def get_patient_from_model(db_id: int) -> Patient:
    patient_model = PatientModel.query.get(db_id)
    return Patient(patient_model.medical_id, PatientParameters(
        blood_group=patient_model.blood,
        acceptable_blood_groups=patient_model.acceptable_blood,
        country_code=patient_model.country,
        hla_antigens=[],  # TODO fill this in from the data
        hla_antibodies=[]  # TODO fill thin in from the data
    ))


def get_donor_from_db(db_id: int) -> Donor:
    pat = get_patient_from_model(db_id)
    return Donor(pat.patient_id, pat.params)


def get_recipient_from_db(db_id: int):
    recipient = get_patient_from_model(db_id)
    related_donors = PatientPairModel.query.filter(PatientPairModel.recipient_id == db_id).all()
    if len(related_donors) == 1:
        don_id = related_donors[0].donor_id
    else:
        raise ValueError(f"There has to be 1 donor per recipient, but {len(related_donors)} "
                         f"were found for recipient with db_id {db_id} and medical id {recipient.patient_id}")
    return Recipient(recipient.patient_id, recipient.params, get_donor_from_db(don_id))


def medical_id_to_id(medical_id: str) -> int:
    patients_with_id = PatientModel.query.filter(PatientModel.medical_id == medical_id).all()
    if len(patients_with_id) == 1:
        return patients_with_id[0].id
    else:
        raise ValueError(f"There has to be 1 patient per medical id, but {len(patients_with_id)} "
                         f"were found for patient with medical id {medical_id}")


def get_all_patients():
    PatientModel.query.filter(PatientModel.active).all()
