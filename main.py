__author__ = 'Jacob Betz'
__email__ = 'euhe@pm.me'

import datetime
from datetime import datetime

from loguru import logger as log
from pathlib import Path

''' Local imports '''
import utils

api_url = 'qualysapi.qg3.apps.qualys.com'
username = ''
password = ''
write_mode = False
_base_path = Path.cwd().joinpath(
    str(datetime.date(datetime.now()))).joinpath('_xml')
xml_input_path = str(_base_path.joinpath('input'))
output_path = str(_base_path.joinpath('output'))

remember_me = False
''' Time difference to use when downloading reports by date '''
report_days_timedelta = 7
''' Max retries to query the Qualys API for the same API request'''
max_retries = 0


def main():
    # 1. Download scans
    # 2. Parse XML reports recursively into a master dataset
    # 3. Export to CSV

    _end_datetime = datetime.now().date()
    _start_datetime = datetime.date(_end_datetime - datetime.timedelta(
        days=int(report_days_timedelta)))
    scan_ids = {}

    log.debug(f'API URL: {str(api_url)} \n'
              f'Start Date: {str(_start_datetime)} \n'
              f'End Date: {str(_end_datetime)}')

    try:
        ''' Downloads VM scans based on datetime'''
        for _id, _title in utils.get_vm_scans_list(url=api_url,
                                                   username=username,
                                                   password=password,
                                                   start_date=_start_datetime,
                                                   end_date=_end_datetime,
                                                   remember_me=remember_me):
            scan_ids[_id] = _title

    except Exception as ex:
        log.exception(f'Could not retrieve VM Scans: {str(ex)}')
        return False

    try:
        log.info(f'Parsing XML reports..')
        dataset = utils.parse_reports(xml_input_path)

        if dataset and write_mode:
            log.info(f'Writing to file..')
            try:
                ''' Determine the write mode and write out to file if given 
                the option '''
                status = utils.write_file(dataset,
                                          write_mode=write_mode,
                                          output_path=output_path)
                if status:
                    log.debug(f'Successfully wrote file using the write_mode: '
                              f'{str(write_mode)}')
                    log.debug(f'Status: {str(status)}')
                    return True
                else:
                    log.error(f'[main] Failed to write to file.')
                    log.debug(f'Status: {str(status)}')
                    return False

            except Exception as ex:
                log.exception(f'Could not write to file: {str(ex)}')
                return False

    except Exception as ex:
        log.exception(f'Could not generate reports: {str(ex)}')
        return False


if __name__ == '__main__':
    main()
