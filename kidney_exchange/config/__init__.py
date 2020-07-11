from kidney_exchange.config.configuration import Configuration, RecipientDonorScore
from kidney_exchange.config.configuration_dto import ConfigurationDto, RecipientDonorScoreDto
from kidney_exchange.database.services.patient_service import medical_id_to_id, id_to_medical_id


def recipient_donor_score_from_dto(self: RecipientDonorScoreDto) -> RecipientDonorScore:
    return RecipientDonorScore(
        medical_id_to_id(self.recipient_medical_id),
        medical_id_to_id(self.donor_medical_id),
        self.compatibility_index
    )


def recipient_donor_score_to_dto(self: RecipientDonorScore) -> RecipientDonorScoreDto:
    return RecipientDonorScoreDto(
        id_to_medical_id(self.recipient_id),
        id_to_medical_id(self.donor_id),
        self.compatibility_index
    )


RecipientDonorScore.to_dto = recipient_donor_score_to_dto
RecipientDonorScoreDto.from_dto = recipient_donor_score_from_dto


def configuration_from_dto(self: ConfigurationDto) -> Configuration:
    return Configuration(
        scorer_constructor_name=self.scorer_constructor_name,
        solver_constructor_name=self.solver_constructor_name,
        enforce_same_blood_group=self.enforce_same_blood_group,
        minimum_compatibility_index=self.minimum_compatibility_index,
        require_new_donor_having_better_match_in_compatibility_index=self.require_new_donor_having_better_match_in_compatibility_index,
        require_new_donor_having_better_match_in_compatibility_index_or_blood_group=self.require_new_donor_having_better_match_in_compatibility_index_or_blood_group,
        use_binary_scoring=self.use_binary_scoring,
        max_cycle_length=self.max_cycle_length,
        max_sequence_length=self.max_sequence_length,
        max_number_of_distinct_countries_in_round=self.max_number_of_distinct_countries_in_round,
        required_patient_ids=self.required_patient_ids,
        manual_recipient_donor_scores=[mrds.from_dto() for mrds in
                                       self.manual_recipient_donor_scores_dtos]
    )


def configuration_to_dto(self: Configuration) -> ConfigurationDto:
    return ConfigurationDto(
        scorer_constructor_name=self.scorer_constructor_name,
        solver_constructor_name=self.solver_constructor_name,
        enforce_same_blood_group=self.enforce_same_blood_group,
        minimum_compatibility_index=self.minimum_compatibility_index,
        require_new_donor_having_better_match_in_compatibility_index=self.require_new_donor_having_better_match_in_compatibility_index,
        require_new_donor_having_better_match_in_compatibility_index_or_blood_group=self.require_new_donor_having_better_match_in_compatibility_index_or_blood_group,
        use_binary_scoring=self.use_binary_scoring,
        max_cycle_length=self.max_cycle_length,
        max_sequence_length=self.max_sequence_length,
        max_number_of_distinct_countries_in_round=self.max_number_of_distinct_countries_in_round,
        required_patient_ids=self.required_patient_ids,
        manual_recipient_donor_scores_dtos=[mrds.to_dto() for mrds in
                                            self.manual_recipient_donor_scores]
    )


Configuration.to_dto = configuration_to_dto
ConfigurationDto.form_dto = configuration_from_dto
