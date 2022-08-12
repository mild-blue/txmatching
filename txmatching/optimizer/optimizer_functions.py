import json
import numpy as np
import pandas as pd

from dacite import from_dict
from io import StringIO
from werkzeug.datastructures import FileStorage

from txmatching.optimizer.compatibility_info import CompatibilityInfo
from txmatching.optimizer.optimizer_config import OptimizerConfig
from txmatching.optimizer.optimizer_return_object import OptimizerReturn


def parse_csv_to_comp_info(csv_content: pd.DataFrame) -> CompatibilityInfo:
    # check data types
    for column in csv_content.columns:
        if csv_content[column].dtype != np.integer:
            raise ValueError(f"Invalid type in column \'{column}\'.")

    # header information
    scoring_column_to_index = {}
    if len(csv_content.columns) > 2:
        for i, header_column in enumerate(csv_content.columns[2:]):
            scoring_column_to_index[header_column] = i

    # compatibility graph
    # todo check that all columns are defined
    compatibility_info = {}
    for _, row in csv_content.iterrows():
        for number in row:
            if number < 0:
                raise ValueError(f"Invalid value {number}, all values must be non-negative.")
        compatibility_info[(int(row[0]), int(row[1]))] = row.values[2:].astype(int).tolist()

    return CompatibilityInfo(
        scoring_column_to_index=scoring_column_to_index,
        compatibility_info=compatibility_info,
    )


def parse_csv_to_pairs(csv_content: pd.DataFrame, comp_info: CompatibilityInfo) -> CompatibilityInfo:
    if len(csv_content.columns) != 2:
        raise ValueError("Invalid \'pairs\' file contents. Length of line not 2.")

    d_to_r_pairs = {}
    non_directed_donors = []
    for _, row in csv_content.iterrows():
        # todo check if ints or NaNs
        if int(row[0]) in d_to_r_pairs or int(row[0]) in non_directed_donors:
            raise ValueError("Invalid \'pairs\' file contents. Duplicate donor.")
        if pd.isnull(row[1]):
            non_directed_donors.append(int(row[0]))
        else:
            d_to_r_pairs[int(row[0])] = int(row[1])

    comp_info.d_to_r_pairs = d_to_r_pairs
    comp_info.non_directed_donors = non_directed_donors
    return comp_info


def parse_json_to_config(json_file: dict) -> OptimizerConfig:
    configuration = from_dict(data_class=OptimizerConfig, data=json_file)
    return configuration


# todo dummy function
def export_return_data() -> OptimizerReturn:
    cycle = {(1, 2): [6, 5, 4, 7], (2, 1): [3, 2, 1, 4]}
    statistics = {"number_of_found_cycles": 1, "number_of_found_transplants": 2}
    return OptimizerReturn(
        cycles_and_chains=[[
            {"donor_id": pair[0], "recipient_id": pair[1], "score": score} for pair, score in cycle.items()
        ]],
        statistics=statistics
    )


def parse_file_storage_to_csv(file: FileStorage) -> pd.DataFrame:
    csv_s = StringIO(file.read().decode("utf-8"))
    return pd.read_csv(csv_s)


def parse_file_storage_to_json(file: FileStorage) -> dict:
    string_json = file.read().decode("utf-8")
    return json.loads(string_json)
