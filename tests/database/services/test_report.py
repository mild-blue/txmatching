import datetime
import difflib
import os
import shutil
import sys

from local_testing_utilities.generate_patients import \
    store_generated_patients_from_folder
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.configuration.configuration import Configuration
from txmatching.database.services import solver_service
from txmatching.database.services.config_service import \
    find_config_db_id_for_configuration_and_data
from txmatching.database.services.report_service import (ReportConfiguration,
                                                         generate_html_report)
from txmatching.database.services.txm_event_service import (
    get_txm_event_complete, get_txm_event_db_id_by_name)
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.get_absolute_path import get_absolute_path

SAMPLE_MATCHING_ID = 1
REPORT_DATETIME_LINE = 556


def generate_report_for_test():
    store_generated_patients_from_folder()
    txm_event_id = get_txm_event_db_id_by_name('high_res_example_data')
    txm_event = get_txm_event_complete(txm_event_id)

    config = Configuration(max_number_of_matchings=5)

    pairing_result = solve_from_configuration(config, txm_event)
    solver_service.save_pairing_result(pairing_result, 1)

    config_id = find_config_db_id_for_configuration_and_data(config, txm_event)

    report_config = ReportConfiguration(0, False)

    path, file_name = generate_html_report(txm_event, config_id, SAMPLE_MATCHING_ID, report_config)
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

        if date_and_time in html_r[REPORT_DATETIME_LINE - 1]:
            html_r[REPORT_DATETIME_LINE - 1] = html_s[REPORT_DATETIME_LINE - 1]
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
