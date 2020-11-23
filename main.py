
__author__ = 'Jacob Betz'

import file_utils as util
from loguru import logger as log

_write_mode = 'print'


def main():
    try:
        ''' get_xml_file_paths iterates over a directory and returns a list of 
            file-paths '''
        for file in util.get_xml_file_paths():
            ''' Test print to see the value of _file_list '''
            log.debug(f'File list, path: {str(file)}')

            try:
                ''' parse_xml returns a Pandas Dataframe '''
                df = util.parse_xml(file_list=file)

                try:
                    ''' Determine the write mode and write out to file if given 
                        the option '''
                    status = util.write_file()

                    if status:
                        log.debug(f'Successfully wrote file using the '
                                  f'write_mode: {str(_write_mode)}')

                    elif status is False:
                        log.error(f'[main] Failed to write to file: '
                                  f'{str(file)}')

                except Exception as ex:
                    log.debug(f'[main] Failed to parse XML: {str(ex)}')
                    return False

            except Exception as ex:
                log.debug(f'[main] Could not parse XML: {str(ex)}')

    except Exception as ex:
        log.debug(f'[main] Could not parse file path(s): {str(ex)}')


if __name__ == '__main__':
    main()
