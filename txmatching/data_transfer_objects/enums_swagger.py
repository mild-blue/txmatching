from txmatching.patients.patient import DonorType
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import Sex
from txmatching.web.api.namespaces import enums_api

CountryCodeJson = enums_api.schema_model('CountryCode', {
    'enum': [country.value for country in Country],
    'type': 'string'
})

BloodGroupEnumJson = enums_api.schema_model('BloodGroupEnum', {
    'enum': [blood_group.value for blood_group in BloodGroup],
    'type': 'string'
})

SexEnumJson = enums_api.schema_model('SexEnum', {
    'enum': [sex.value for sex in Sex],
    'type': 'string',
    'description': 'Sex of the patient.'
})

DonorTypeEnumJson = enums_api.schema_model('DonorType', {
    'enum': [donor_type.value for donor_type in DonorType],
    'type': 'string',
    'description': 'Type of the donor.'
})
