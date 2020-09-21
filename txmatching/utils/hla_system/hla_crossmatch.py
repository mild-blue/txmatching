from typing import Optional

from txmatching.patients.patient_parameters import HLAAntigens, HLAAntibodies
from txmatching.utils.hla_system.hla_table import all_splits_for_broad, broad_for_split, is_split


def is_positive_hla_crossmatch(donor_antigens: HLAAntigens,
                               recipient_antibodies: HLAAntibodies,
                               crossmatch_in_split_resolution: bool) -> bool:
    """
    Do donor and recipient have positive crossmatch in HLA system?
    If this can't be determined, return None
    e.g. A23 -> A23 True
         A9 -> A9  True -- A9 in antibodies indicates wider range of antibodies, in this case A23, A24
         A23 -> A9 True
         A23 -> A24 False
         A9 -> A23 None -- A9 in antigens indicates incomplete information
    :param donor_antigens: donor antigens to crossmatch
    :param recipient_antibodies: recipient antibodies to crossmatch
    :param crossmatch_in_split_resolution: setting whether to use split resolution for crossmatch determination
    :return:
    """
    if crossmatch_in_split_resolution:
        # in case some code is in broad resolution we treat is as if both split resolution codes were present
        donor_antigens_set = {split_code for code in donor_antigens.codes for split_code in
                              all_splits_for_broad.get(code, [code])}
        recipient_antibodies_set = {split_code for code in recipient_antibodies.codes for split_code in
                                    all_splits_for_broad.get(code, [code])}
    else:
        donor_antigens_set = {broad_for_split.get(code, code) for code in donor_antigens.codes}
        recipient_antibodies_set = {broad_for_split.get(code, code) for code in recipient_antibodies.codes}

    common_codes = recipient_antibodies_set.intersection(donor_antigens_set)
    # if there are any common codes, positive crossmatch is found
    return len(common_codes) > 0


def is_positive_hla_crossmatch_obsolete(donor_antigens: HLAAntigens,
                                        recipient_antibodies: HLAAntibodies) -> Optional[bool]:
    """
    Do donor and recipient have positive crossmatch in HLA system?
    If this can't be determined, return None
    e.g. A23 -> A23 True
         A9 -> A9  True -- A9 in antibodies indicates wider range of antibodies, in this case A23, A24
         A23 -> A9 True
         A23 -> A24 False
         A9 -> A23 None -- A9 in antigens indicates incomplete information
    :param donor_antigens:
    :param recipient_antibodies:
    :return:
    """
    positive_crossmatch = True
    negative_crossmatch = False
    crossmatch_cant_be_determined = None

    recipient_antibodies = recipient_antibodies.codes
    recipient_antibodies_with_splits = list(recipient_antibodies)

    for antibody_code in recipient_antibodies:
        split_codes = all_splits_for_broad.get(antibody_code)
        if split_codes is not None:
            recipient_antibodies_with_splits.extend(split_codes)

    crossmatch_cant_be_determined_so_far = False

    for antigen_code in donor_antigens.codes:
        code_is_split = is_split(antigen_code)

        if code_is_split is True or code_is_split is None:  # Code is split or we don't know
            if antigen_code in recipient_antibodies_with_splits:
                return positive_crossmatch
        else:  # Code is broad
            if antigen_code in recipient_antibodies:
                return positive_crossmatch

            antigen_splits = all_splits_for_broad.get(antigen_code)
            if antigen_splits is not None:
                for antigen_split in antigen_splits:
                    if antigen_split in recipient_antibodies:
                        crossmatch_cant_be_determined_so_far = True

    if crossmatch_cant_be_determined_so_far is True:
        return crossmatch_cant_be_determined

    return negative_crossmatch
