__author__ = 'Jacob Betz'
__email__ = 'euhe@pm.me'

from pathlib import Path
from datetime import datetime
from loguru import logger as log
from lxml import objectify, etree
import pandas as pd

import qualysapi as api

''' Set the columns to ignore here '''
_ignore_columns = None

''' Set the xml directory to read from and output path to write to '''
_output_dir_name = 'output'
_xml_input_dir_name = '_xml_input'
_base_path = Path.cwd().joinpath(
    str(datetime.date(datetime.now()))).joinpath('_xml')
_xml_input_path = str(_base_path.joinpath('input'))
_output_path = str(_base_path.joinpath('output'))

''' _write_mode can be `print`, `csv`, `json`, or `all`. '''
_write_mode = 'print'
_max_retries = 0


# def get_dtd(url, api_type):
#    if url is not None or '':
#        try:

#    return False


# def validate_xml_response(xml_data=None, xml_dtd=None):
''' TODO:
    Validates the XML data against it's XML DTD and returns True if it
    matches the DTD or False if it does not.
:param xml_data:
:param xml_dtd:
:return: True if xml_data matches the XML DTD or False if it does not
'''

#    return False


def query(url=None,
          params=None,
          username=None,
          password=None,
          remember_me=False,
          max_retries=_max_retries):

    _pc_scans_suffix = '/api/2.0/fo/scan/compliance'
    _pc_scans_list_dtd = ''

    if url is None or '':
        return False
    if params is None or '':
        return False
    if username is None or '':
        return False
    if password is None or '':
        return False
    else:
        _username = str(username)
        _password = str(password)

    try:
        ''' Create the API request if _suffix is valid based on API type'''
        with api.connect(hostname=url,
                         username=_username,
                         password=_password,
                         remember_me=remember_me,
                         max_retries=max_retries) as cnn:
            try:
                ''' Send the crafted API request '''
                with cnn.request(api_call=url,
                                 data=params,
                                 api_version='2.0',
                                 http_method='post') as response:
                    # TODO: Validate XML Reponse with DTD here
                    # If ok, pass response, response.status
                    return etree.fromstring(response.encode('utf-8')), \
                           response.status

            except Exception as ex:
                log.exception(f'Could not submit request to the Qualys API: '
                              f'{str(ex)}')
                return False

    except Exception as ex:
        log.exception(f'Could not use qualysapi to connect to Qualys API: '
                      f'{str(ex)}')
        return False


def download_vm_scan(url='',
                     connection_limit=2):

    return


def get_vm_scans_list(url='qualysapi.qualys.com',
                      username=None,
                      password=None,
                      start_date=None,
                      end_date=None,
                      remember_me=False,
                      max_retries=_max_retries):

    _vm_scans_suffix = '/api/2.0/fo/scan'
    _vm_scans_list_dtd = '/api/2.0/fo/scan_list_output.dtd'

    if start_date is None or '':
        log.error(f'Start date is empty.')
        return False
    if end_date is None or '':
        log.error(f'End date is empty.')
        return False

    _api_call = str(url) + _vm_scans_suffix
    _params = {
        'action': 'list',
        'launched_after_datetime': start_date,
        'launched_before_datetime': end_date,
    }

    try:
        response, status = query(_api_call,
                                 _params,
                                 username,
                                 password,
                                 remember_me=remember_me,
                                 max_retries=max_retries)
        log.debug(f'Status Code: {str(status)}')

        if status:
            for item in response.iter(tag=''):
                yield item.value
        else:
            log.error(f'Query returned a false status: {str(status)}')
            log.debug(f'Response: {str(response)}')

    except Exception as ex:
        log.exception(f'Could not query the Qualys API: {str(ex)}')
        return False


def get_xml_header_title(xml_data=None, file_path=None):
    if xml_data:
        with objectify.parse(str(xml_data)).getroot() as xml_root:
            for key in xml_root.find('HEADER'):
                yield key.findtext('TITLE')

    elif Path.is_file(file_path):
        with objectify.parse(open(file_path)).getroot() as root:
            for key in root.find('HEADER'):
                yield key.findtext('TITLE')

    else:
        log.error(f'Failed to get scans data Title. ')
        return False


def parse_root(root=None, include=None, skip_fields=None):
    '''
        Recursively parses XML document root object elements and their children.

    :param root: XML document root object. If None, this function returns False
    :param list include: If None, all fields are included. If `include`
    has a string or list, we only return included elements.
    :param list skip_fields: If None, no fields are skipped. If `skip_fields`
    has a string or list, we return all elements except the `skip_fields`
    fields.
    :return: list - data
    '''
    if root is not None:
        if include is not None:
            ''' Filter for included fields'''
            data = []
            _include = list(include)

            for element in root.getchildren():
                el_data = {}
                if element.tag in _include:
                    el_data[element.tag] = element.pyval
                else:
                    continue

                for child in element.getchildren():
                    if child.tag in _include:
                        el_data[child.tag] = child.pyval
                    else:
                        continue
                data.append(el_data)
            return data

        elif skip_fields is not None:
            ''' Filter for skipped fields '''
            data = []
            _skip_fields = list(skip_fields)

            for element in root.getchildren():
                el_data = {}
                if element.tag in _skip_fields:
                    continue

                for child in element.getchildren():
                    if child.tag in _skip_fields:
                        continue
                    el_data[child.tag] = child.pyval
                data.append(el_data)

            return data

    if root is not None:
        ''' Returns a list of dictionaries from the text and attributes of 
        the children under the XML root'''
        log.debug(f'Doing regular parsing without filters..')
        return [parse_xml_element(child) for child in root.getchildren()]
    else:
        log.error(f'`root` parameter input is invalid.')


def parse_xml_element(element=None, parsed=None):
    '''
        Collect {key:attribute} and {tag:text} from this XML element and all
        of it's children into a single dictionary of strings.

    :param element:
    :param parsed:
    :return:
    '''
    if parsed is None:
        parsed = dict()

    for key in element.keys():
        if key not in parsed:
            parsed[key] = element.attrib.get(key)
        if element.text:
            parsed[element.tag] = element.text
        else:
            raise ValueError(f'Duplicate attribute {key} at element '
                             f'{element.getroottree().getpath(element)}')
    ''' Apply recursion '''
    for child in list(element):
        parse_xml_element(child, parsed)
    return parsed


def parse_xml_report(xml_file_directory=None):
    '''
        Recursively parses a a single or multiple XML files in a given
        file_path. If file_path is None or Empty, parse_xml_files parses XML data if
        xml_data is not None.
        Returns False on failure to parse

    :param str directory: A file path
    :return: Pandas DataFrame master_df converted from raw XML data
    '''

    headers_df = pd.DataFrame()
    master_df = pd.DataFrame()

    log.debug(f'File path: {str(xml_file_directory)}')

    if not Path.is_file(Path(xml_file_directory)):
        ''' Skip the file path if it isn't a file for some reason'''
        log.error(f'File path is not a file: {str(xml_file_directory)}')
        return False
    else:
        log.debug(f'Parsing file: {str(xml_file_directory)}')
        try:
            with objectify.parse(open(str(xml_file_directory))) as xml:
                ''' Parse the XML from file and get the XML data root '''
                try:
                    data = parse_root(xml, skip_fields=['SCAN', 'HEADER'])
                    log.debug(f'Parsed data from root')

                    try:
                        headers = parse_root(xml, include=['HEADER'])
                        log.debug(f'Headers data: \n {str(headers)}')

                        # TODO: data + headers for each IP

                    except Exception as ex:
                        log.exception(f'Could not append headers to headers '
                                      f'dataframe: {str(ex)}')

                except Exception as ex:
                    log.exception(f'Could not parse xml data: {str(ex)}')

        except Exception as ex:
            log.exception(f'Could not parse root: {str(ex)}')

        return master_df, headers_df


def get_xml_file_paths(directory=_xml_input_path):
    '''
        A generator function that iterates over file paths in a `directory` and
        returns those xml file paths.
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

                elif file.is_file():
                    if file.suffix == '.xml' or 'xml':
                        yield str(file)
                else:
                    log.error(f'file is not a directory or file.')

        except Exception as ex:
            log.debug(f'[get_xml_file_paths] Failed to read directory for '
                      f'files: {str(ex)}')


def parse_reports(xml_input_directory=_xml_input_path):
    '''
        Recursively gets a list of paths to XML files residing in
        xml_input_directory. For each XML report path, parse_xml_report is
        called to parse each document, and if it doesn't return False,
        the returned data will be appended to the master dataframe.
    :param xml_input_directory:
    :return: DataFrame master_df: Returns compiled XML reports as Pandas
    DataFrame objects and False if this function fails.
    '''
    master_df = pd.DataFrame()

    try:
        ''' get_xml_file_paths iterates over a directory and returns a list of 
            file-paths '''
        for file in get_xml_file_paths(directory=str(xml_input_directory)):
            ''' Test print to see the value of file '''
            log.debug(f'File list, path: {str(file)}')

            try:
                data = parse_xml_report(xml_file_directory=file)

                if data:
                    master_df.append(data)
                else:
                    continue

            except Exception as ex:
                log.exception(f'[main] Failed to parse XML: {str(ex)}')
                return False

        return master_df

    except Exception as ex:
        log.debug(f'[main] Could not parse file path(s): {str(ex)}')


def write_file(data=None, write_mode=_write_mode, output_path=_output_path,
               ignore_columns=False):
    '''

    :param pandas.DataFrame data: A Pandas DataFrame object
    :param write_mode: Can be `print`, `csv`, `json`, or `all`.
    :param str output_path: Output path of the file
    :param list ignore_columns: List of column names to ignore in data Pandas
        DataFrame: ignore_columns = ['CVSS3', 'CVSS', ...]
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
    if ignore_columns:
        # TODO: Drop columns here
        log.debug(f'ignore_columns is True')

    ''' If the output_path is not a directory, assign _file_path as a default 
        file path location'''
    if not Path(output_path).is_dir():
        try:
            Path.mkdir(Path(output_path))

        # TODO: Elaborate on exceptions
        except Exception as ex:
            log.exception(f'Could not make directory: {str(ex)}')

    if Path.is_dir(Path(output_path)):
        _file_path = str(output_path)

        if write_mode is None or '':
            log.debug(f'[write_file] write_mode is None or Empty.. '
                      f'cannot continue: {str(write_mode)}.')
            return False

        if write_mode == 'print' or 'all':
            try:
                for line in data:
                    log.debug(line)

            # TODO: Elaborate on exceptions
            except Exception as ex:
                log.exception(f'[parse_xml_files] Could not print: {str(ex)}')
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
        if write_mode == 'json' or 'all':
            try:
                if write_file(data=data, write_mode='json',
                              output_path=output_path):
                    log.debug(f'Completed XML parsing to JSON')
                    return True
                else:
                    log.debug(f'Failed to write JSON. ')
                    return False

            except Exception as ex:
                log.debug(
                    f'[parse_xml_files] Could not write out to JSON: {str(ex)}')
                return False