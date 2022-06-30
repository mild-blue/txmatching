import datetime
import difflib
import os
import shutil
import sys

from local_testing_utilities.generate_patients import \
    store_generated_patients_from_folder
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.database.services.config_service import \
    save_config_parameters_to_db
from txmatching.database.services.pairing_result_service import \
    solve_from_configuration_and_save
from txmatching.database.services.report_service import (ReportConfiguration,
                                                         generate_html_report)
from txmatching.database.services.txm_event_service import (
    get_txm_event_complete, get_txm_event_db_id_by_name)
from txmatching.utils.get_absolute_path import get_absolute_path

SAMPLE_MATCHING_ID = 1
REPORT_DATETIME_LINE = 585


def generate_report_for_test():
    store_generated_patients_from_folder()
    txm_event_id = get_txm_event_db_id_by_name('high_res_example_data')
    txm_event = get_txm_event_complete(txm_event_id)

    configuration_parameters = ConfigParameters(max_number_of_matchings=5)
    configuration = save_config_parameters_to_db(
        config_parameters=configuration_parameters,
        txm_event_id=txm_event_id,
        user_id=1
    )

    pairing_result_model = solve_from_configuration_and_save(configuration, txm_event)

    report_config = ReportConfiguration(0, False)

    path, file_name = generate_html_report(
        txm_event, configuration.id, pairing_result_model,
        SAMPLE_MATCHING_ID, report_config
    )
    result_html_full_path = path + '/' + file_name
    return result_html_full_path


class TestReport(DbTests):

    def test_generate_html_report(self):

        sample_html_full_path = get_absolute_path('tests/resources/sample_html_report.html')

        # uncomment those two lines if you need to generate
        # a new sample report and run test,
        # then don't forget to comment lines back

        # file_full_path = generate_report_for_test()
        # shutil.move(file_full_path, sample_html_full_path)

        result_html_full_path = generate_report_for_test()

        date_and_time = datetime.datetime.now().strftime('%b %d, %Y %H:%M')

        with open(sample_html_full_path, 'r', encoding='utf-8') as file_s:
            html_s = file_s.readlines()
        with open(result_html_full_path, 'r', encoding='utf-8') as file_r:
            html_r = file_r.readlines()

        if date_and_time in html_r[REPORT_DATETIME_LINE]:
            html_r[REPORT_DATETIME_LINE] = html_s[REPORT_DATETIME_LINE]
        # else: you may have forgotten to change HTML_DATETIME_LINE
        #       when you changed the report template

        self.assertEqual(html_s, html_r)

        # print diffs
        diff = difflib.unified_diff(
            html_s,
            html_r,
            fromfile='file_s',
            tofile='file_r',
            n=0
        )
        for line in diff:
            sys.stdout.write(line)

        os.remove(result_html_full_path)
