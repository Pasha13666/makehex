import logging
from sys import argv
from makehex.lexer import lex
from makehex.parser import parser
from makehex.config import parse_config

_stream_handler = logging.StreamHandler()
_stream_handler.setLevel(logging.WARNING)
_stream_handler.setFormatter(logging.Formatter("%(levelname)s [%(asctime)s] %(filename)-15s %(message)s"))
logging.root.addHandler(_stream_handler)

_stop_msg = "{0} Program stopped! {0}".format('=' * 15)

# noinspection PyBroadException
try:
    if len(argv) < 3 or '--help' in argv or '-h' in argv:
        print("Usage: makehex INPUT_FILE OUTPUT_FILE [CONFIG_FILE]")

    with open(argv[1]) as input_file, open(argv[2], "wb+") as output_file:
        co = parse_config(argv[3] if len(argv) >= 4 else None)
        logging.debug("input file: %s; output file: %s", input_file.name, output_file.name)
        parser()(lex(input_file.read()), 0).value.write(output_file, *co)

except:
    logging.exception(_stop_msg)
else:
    logging.debug(_stop_msg)
