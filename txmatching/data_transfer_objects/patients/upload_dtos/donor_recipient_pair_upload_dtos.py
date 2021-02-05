from dataclasses import dataclass

from txmatching.data_transfer_objects.patients.upload_dtos.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.utils.country_enum import Country


@dataclass
class DonorRecipientPairDTO:
    country_code: Country
    donor: DonorUploadDTO
    recipient: RecipientUploadDTO
