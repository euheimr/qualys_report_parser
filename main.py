
__author__ = 'Jacob Betz'
__email__ = 'euhe@pm.me'

from loguru import logger as log

''' Local imports '''
import utils
#import config

_write_mode = 'print'


def main():
    #try:
    #    config.read_config()
    #except Exception as ex:
    #    log.exception(f'Could not read config: {str(ex)}')

    try:
        utils.parse_reports()
    except Exception as ex:
        log.exception(f'Could not generate reports: {str(ex)}')


if __name__ == '__main__':
    main()
