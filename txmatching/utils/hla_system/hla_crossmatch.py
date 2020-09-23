from txmatching.patients.patient_parameters import HLAAntibodies, HLATyping
from txmatching.utils.hla_system.hla_table import (broad_to_split, split_to_broad)


def is_positive_hla_crossmatch(donor_hla_typing: HLATyping,
                               recipient_antibodies: HLAAntibodies,
                               use_split_resolution: bool) -> bool:
    """
    Do donor and recipient have positive crossmatch in HLA system?
    e.g. A23 -> A23 True
         A9 -> A9  True
         A23 -> A9 True
         A23 -> A24 False if use_split_resolution else True
         A9 -> A23 True
         A9 broad <=> A23, A24 split
    :param donor_hla_typing: donor hla_typing to crossmatch
    :param recipient_antibodies: recipient antibodies to crossmatch
    :param use_split_resolution: setting whether to use split resolution for crossmatch determination
    :return:
    """
    if use_split_resolution:
        # in case some code is in broad resolution we treat it is as if all split resolution codes were present
        donor_hla_typing_set = {split_code for code in donor_hla_typing.codes for split_code in
                                broad_to_split(code)}
        recipient_antibodies_set = {split_code for code in recipient_antibodies.codes for split_code in
                                    broad_to_split(code)}
    else:
        donor_hla_typing_set = {split_to_broad(code) for code in donor_hla_typing.codes}
        recipient_antibodies_set = {split_to_broad(code) for code in recipient_antibodies.codes}

    common_codes = recipient_antibodies_set.intersection(donor_hla_typing_set)
    # if there are any common codes, positive crossmatch is found
    return len(common_codes) > 0
