
__author__ = 'Jacob Betz'
__email__ = 'euhe@pm.me'

from loguru import logger as log
from pathlib import Path
from configparser import ConfigParser

''' Set the config file name and directory '''
_config_file_name = 'qls.cfg'
_config_path = str(Path.cwd().joinpath(_config_file_name))


def write_config(path=_config_path, hostname=None, username=None,
                 password=None):
    try:
        with ConfigParser() as parser:
            parser.add_section('main')
            parser.set('DEFAULT', 'hostname', hostname)

            # TODO: add other sections to the config output
            parser.add_section('username')
            parser.set('DEFAULT', 'username', username)

            parser.add_section('password')
            parser.set('DEFAULT', 'password', password)

            # TODO: Write out config to disk
            parser.write(path)

    except Exception as ex:
        log.exception(f'Could not create ConfigParser object: {str(ex)}')


def read_config(path=_config_path):
    '''
        Reads a config file and returns
    :param path:
    :return:
    '''

    if Path.is_dir(Path(path)):
        log.debug(f'Path is a directory.. appending default configuration '
                  f'file name')
        _path = Path(path).joinpath(_config_file_name)

    elif Path.is_file(Path(path)):
        if path.endswith('.cfg'):
            log.debug(f'Path is a config file: {str(path)}')
            _path = Path(path)

            try:
                with ConfigParser as cfg:
                    cfg.read(filenames=str(_path))

                    if cfg.has_option('DEFAULT', 'hostname'):
                        hostname = cfg.get('DEFAULT', 'hostname')

                    if cfg.has_option('DEFAULT', 'username'):
                        username = cfg.get('DEFAULT', 'username')

                    if cfg.has_option('DEFAULT', 'password'):
                        password = cfg.get('DEFAULT', 'password')

                    log.debug(cfg.items('DEFAULT'))
                    return hostname, username, password

            except Exception as ex:
                log.exception(f'Could not read config file: {str(ex)}')

        else:
            log.error(f'Config file path does not end with .cfg: {str(path)}')
            return False

    elif not Path.is_file(Path(path)):
        try:
            ''' If the config file does not exist, write a new config. '''
            if write_config(path):
                return True

        except Exception as ex:
            log.exception(f'Could not create create or write the config file: '
                          f'{str(ex)}')
    else:
        return False