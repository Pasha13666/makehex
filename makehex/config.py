import logging
import os
from logging.handlers import RotatingFileHandler
from configparser import ConfigParser
from makehex.globals import Globals
from makehex.log import DebugLogRecord


if os.name == 'posix' or os.name == 'mac':
    _DEFAULTS = {
        'log_file': '/var/log/makehex.log',
        'include_dir': '/usr/lib/makehex/include',
        'config_file': '/etc/makehex.ini',
        'file_encoding': 'UTF-8',
    }
elif os.name == 'nt' or os.name == 'os2':
    _DEFAULTS = {
        'log_file': r'C:\\makehex\makehex.log',
        'include_dir': r'C:\\makehex\include',
        'config_file': r'C:\\makehex\makehex.ini',
        'file_encoding': 'cp866'
    }
else:
    _DEFAULTS = {
        'log_file': 'makehex.log',
        'include_dir': 'include',
        'config_file': 'makehex.ini',
        'file_encoding': 'ASCII'
    }


def parse_config(name: str):
    parser = ConfigParser(default_section='makehex', allow_no_value=True)
    parser.read(name if name else _DEFAULTS['config_file'])
    d = parser.defaults()

    def lrf(*args, **kwargs):
        if args[1] == 1:
            return DebugLogRecord(*args, **kwargs)
        return orf(*args, **kwargs)

    file_handler = RotatingFileHandler(parser.get('log', 'file', fallback=_DEFAULTS['log_file']), 'a', 1024 * 1024, 5)
    file_handler.setLevel(parser.getint('log', 'level', fallback=3) * 10)
    file_handler.setFormatter(logging.Formatter("[{levelname:^8s}|{asctime}|{module:^10s}:{lineno:>3d}|{funcName:^15}] {message}",
                                                style='{'))
    orf = logging.getLogRecordFactory()
    logging.setLogRecordFactory(lrf)
    logging.root.addHandler(file_handler)
    logging.root.setLevel(0)

    libs = {}
    for library in parser["libraries"]:
        logging.debug("Loading library %s...", library)
        conf = ConfigParser()
        conf.read(library)
        for selection in conf.sections():
            for k, v in conf[selection].items():
                libs[k] = (os.path.join(os.path.dirname(library), selection), v)
                logging.debug("Loaded %s", k)

    return {
        "ENCODING": d.get('file_encoding', _DEFAULTS['file_encoding']),
        "ENDIAN": d.get('endian', 'little'),
        "ALIGN": "OFF",
        "INCLUDE_DIR": d.get('include_dir', _DEFAULTS['include_dir'])
    }, Globals(libs)

