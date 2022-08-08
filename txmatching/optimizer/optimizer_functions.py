import json
import numpy as np
import pandas as pd
import zipfile

from dacite import from_dict
from flask import Response, send_file
from io import BytesIO, StringIO
from werkzeug.datastructures import FileStorage

from txmatching.optimizer.compatibility_info import CompatibilityInfo
from txmatching.optimizer.optimizer_config import OptimizerConfig


def parse_csv_to_comp_info(csv_file: FileStorage) -> CompatibilityInfo:
    csv_s = csv_file.read().decode("utf-8")
    csv_content = pd.read_csv(StringIO(csv_s))

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
        compatibility_info[(int(row[0]), int(row[1]))] = row.values[2:].astype(int).tolist()

    return CompatibilityInfo(
        scoring_column_to_index=scoring_column_to_index,
        compatibility_info=compatibility_info,
    )


def parse_csv_to_pairs(csv_file: FileStorage, comp_info: CompatibilityInfo) -> CompatibilityInfo:
    csv_s = csv_file.read().decode("utf-8")
    csv_content = pd.read_csv(StringIO(csv_s))

    if len(csv_content.columns) != 2:
        raise ValueError("Invalid \'pairs\' file contents. Length of line not 2.")

    for column in csv_content.columns:
        if csv_content[column].dtype != np.integer:
            raise ValueError(f"Invalid type in column \'{column}\'.")

    d_to_r_pairs = {}
    non_directed_donors = []
    for _, row in csv_content.iterrows():
        if row[0] in d_to_r_pairs or row[0] in non_directed_donors:
            raise ValueError("Invalid \'pairs\' file contents. Duplicate donor.")
        # todo how to check for non directed donors? recipient is set to -1 or is it line of length 1?
        if row[1] == -1:
            non_directed_donors.append(row[0])
        else:
            d_to_r_pairs[int(row[0])] = int(row[1])

    comp_info.d_to_r_pairs = d_to_r_pairs
    comp_info.non_directed_donors = non_directed_donors
    return comp_info


def parse_json_to_config(json_file: FileStorage) -> OptimizerConfig:
    string_json = json_file.read().decode("utf-8")
    dict_json = json.loads(string_json)
    configuration = from_dict(data_class=OptimizerConfig, data=dict_json)
    return configuration


# todo return csv rather than excel and use pandas
def export_return_data() -> Response:
    cycles_column_names = ['donor_id', 'recipient_id', 'cycle_or_chain_id', 'index_in_cycle', 'weighted_score']
    selected_cycles = [[1, 4, 1, 0, 15], [2, 7, 1, 1, 12]]

    stats_column_names = ['level_of_optimization', 'prio_highly_sensitized_recipients', 'max_num_of_transplants',
                          'number_of_patients']
    matching_stats = [[1, 5, 4, 6], [2, 2, 5, 8]]

    df_selected_cycles = pd.DataFrame(selected_cycles, columns=cycles_column_names)
    df_matching_stats = pd.DataFrame(matching_stats, columns=stats_column_names)

    output_file = BytesIO()
    with zipfile.ZipFile(output_file, 'w', compression=zipfile.ZIP_DEFLATED) as csv_zip:
        csv_zip.writestr("selected_cycles.csv", df_selected_cycles.to_csv())
        csv_zip.writestr("matching_stats.csv", df_matching_stats.to_csv())

    output_file.seek(0)

    return send_file(
        path_or_file=output_file,
        as_attachment=True,
        attachment_filename='output.zip',
        cache_timeout=0
    )
