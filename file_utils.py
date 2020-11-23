from pathlib import Path
from loguru import logger as log
import xml.etree.ElementTree as ET
import xmltodict
import pandas as pd

''' Set the columns to ignore here '''
_ignore_columns = None

''' Set the xml directory to read from and output path to write to '''
_output_path = Path.cwd().joinpath('output')
_xml_directory = Path.cwd().joinpath('scan-data-xml')

''' _write_mode can be `print`, `csv`, `json`, or `all`. '''
_write_mode = 'print'


def get_xml_file_paths(directory=_xml_directory):
    '''
        A generator function that iterates over file paths in a `directory` and
        returns those file directories or paths.

    :param str directory: Set a directory or file path to look for XML files
    :return: dict or a single file path string
    '''

    if directory is None or '':
        log.debug(f'[get_xml_file_paths] Parameter directory is None, cannot '
              f'continue.')
        return False

    else:
        try:
            file_list = [f for f in Path.iterdir(Path(directory))]

            for file in file_list:
                if file.is_dir():
                    continue

                if file.is_file():
                    yield str(file)

        except Exception as ex:
            log.debug(f'[get_xml_file_paths] Failed to read directory for '
                      f'files: {str(ex)}')


def validate_xml(xml_data=None):
    '''
        Validates the XML data against it's XML DTD and returns True if it
        matches the DTD or False if it does not.
    :param xml_data:
    :return: True if xml_data matches the XML DTD or False if it does not
    '''

    return False


def parse_xml(file_list=None):
    '''

    :param dict file_list:
    :return: A new Pandas DataFrame converted from XML
    '''

    if file_list is None or '':
        raise Exception(f'[parse_xml] Parameter xml_data is None, cannot '
                        f'continue.')

    _new_df = pd.DataFrame()
    _headers = pd.DataFrame()

    ''' Recursively parse the files with xmltodict in the file_list '''
    for file in file_list:
        if not Path.is_file(Path(file)):
            log.error(f'File path is not a file!')

        else:
            log.debug(f'Parsing file: {str(file)}')

            try:
                ''' Parse the XML from file and get the XML data root node '''
                xml_data = ET.parse(str(file)).getroot()

                ''' Find the headers in the ElementTree object and recursively 
                    iterate over the children of `HEADER`'''
                for header in xml_data.iter('HEADER'):
                    try:
                        ''' Append the header of the data '''
                        _headers.append(header)

                        ''' Remove the header from the main dataset'''
                        xml_data.remove(header)

                        ''' Append the headers information as new columns '''
                        #xml_data.insert

                    except Exception as ex:
                        log.exception(f'[parse_xml] Could not append header: '
                                      f'{str(ex)}')

                try:
                    ''' Convert the XML data to string while enforcing a UTF-8 
                    encoding '''
                    xml_str = ET.tostring(xml_data,
                                          encoding='utf-8',
                                          method='xml')
                    #headers_str = ET.tostringlist()

                    try:
                        # TODO: Ignore/drop columns option?

                        ''' Convert the XML string to a dictionary '''
                        _new_df.append(xmltodict.parse(xml_input=xml_str,
                                                       process_namespaces=True))

                        # TODO: For each report, get the scan headers and append
                        #  the data from the headers to the _new_df pandas
                        #  DataFrame as columns

                    except Exception as ex:
                        log.exception(f'[parse_xml] Could not convert the XML '
                                      f'data to string: {str(ex)}')
                except Exception as ex:
                    log.exception(f'[parse_xml] Could not convert the XML '
                                  f'data to string: {str(ex)}')

            except Exception as ex:
                log.exception(f'[parse_xml] Could not parse file: {str(ex)}')
                return False

    return _new_df, _headers


def write_file(data=None, write_mode=_write_mode, output_path=_output_path,
               ignore_columns=_ignore_columns):
    '''

    :param obj data:
    :param write_mode: Can be `print`, `csv`, `json`, or `all`.
    :param str output_path:
    :param list ignore_columns:
    :return bool: True when any write is successful. False when writing to
    any file fails.
    '''

    if data is None or '':
        log.debug(f'[write_file] Parameter `data` is None or empty, cannot '
                  f'continue.')
        return False

    if output_path is None or '':
        log.error(f'[write_file] Parameter output_path is None or empty, '
                  f'cannot continue.')
        return False

    ''' If ignore_columns has values, drop the columns according to the list 
        of names in ignore_columns. '''
    # if ignore_columns is not None or '':
        # TODO: Drop columns here

    ''' If the output_path is not a directory, assign _file_path as a default 
        file path location'''
    if not Path(output_path).is_dir():
        try:
            Path.mkdir(Path(output_path))

        # TODO: Elaborate on exceptions
        except Exception as ex:
            log.exception(f'Could not make directory _output_')

    if Path.is_dir(Path(output_path)):
        _file_path = str(output_path)

        if write_mode is None or '':
            log.debug(f'[write_file] write_mode is None or Empty string.. '
                      f'cannot continue: {str(write_mode)}.')
            return False

        if write_mode == 'print' or 'all':
            try:
                for line in data:
                    log.debug(line)

            # TODO: Elaborate on exceptions
            except Exception as ex:
                log.exception(f'[parse_xml] Could not print: {str(ex)}')
                return False

        if write_mode == 'csv' or 'all':
            try:
                ''' Write Pandas DataFrame to CSV using _file_path derived 
                from output_path '''
                pd.DataFrame.to_csv(data, _file_path)
                log.debug(f'Wrote DataFrame to csv: {str(_file_path)}')

            # TODO: Elaborate on exceptions
            except Exception as ex:
                log.exception(f'Could not write Pandas DataFrame to csv:'
                              f' {str(ex)}')
                return False

        # TODO: Export / write out data structure to JSON file(s)
        # if write_mode == 'json' or 'all':
        #    try:
        #        #if write_json(_new_dict, output_path):
        #        return True

        #        #else:
        #        #    log.debug(f'Failed to write JSON. ')
        #        #    return False

        #    except Exception as ex:
        #        log.debug(f'[parse_xml] Could not write out to JSON: '
        #                  f'{str(ex)}')
        #        return False

        log.debug(f'Completed XML parsing.')
        return True

