from kidney_exchange.config.configuration import Configuration
from kidney_exchange.filters.filter_base import FilterBase
from kidney_exchange.filters.filter_default import FilterDefault
from kidney_exchange.patients.patient import Patient


def make_filter_from_config(configuration: Configuration) -> FilterBase:
    # TODO: When we add more filters, add similar logic as for make_solver and make_scorer from config
    transplant_filter = FilterDefault(max_cycle_lenght=configuration.max_cycle_length,
                                      max_sequence_lenght=configuration.max_sequence_length,
                                      max_number_of_distinct_countries_in_round=configuration.max_number_of_distinct_countries_in_round,
                                      required_patients=[Patient(patient_id) for patient_id in
                                                         configuration.required_patient_ids])
    return transplant_filter


if __name__ == "__main__":
    config = Configuration()
    filter_made_from_config = make_filter_from_config(config)
    print(filter_made_from_config)
