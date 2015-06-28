#!/usr/bin/env python

"""ksgen generates settings based on the settings directory.

 Usage:
    ksgen -h | --help
    ksgen [options] <command> [<args> ...]

 Options:
    --log-level=<log-level>     Log levels: debug, info, warning
                                            error, critical
                                [default: warning]
    --config-dir=<PATH>         Settings directory path.
                                If given, overrides the 'KHALEESI_SETTINGS'
                                environment variable.

 Commands:
     help
     generate
"""

from __future__ import print_function
from ksgen import docstring, log_color, settings, yaml_utils
from docopt import docopt
from os import environ
from os import path
import logging
import sys


def usage(path):
    doc_string = "{docs} \n Valid configs are: {config}".format(
        docs=__doc__,
        config=docstring.Generator(path).generate())
    print(doc_string)


def _setup_logging(level):
    log_color.enable()
    numeric_val = getattr(logging, level.upper(), None)
    if not isinstance(numeric_val, int):
        raise ValueError("Invalid log level: %s" % level)
    fmt = ("%(filename)s:%(lineno)3s| "
           "%(funcName)20s() |%(levelname)8s: %(message)s")
    logging.basicConfig(level=numeric_val, format=fmt)


def get_config_dir(args):
    """load the path for configuration tree.

    search order:
        1. args
        2. environment variable KHALEESI_SETTINGS

    :param args: module input arguments
    :raises: ValueError if path is missing or doesn't exist.
    :return: path to configuration tree
    """

    config_dir = args["--config-dir"] or environ.get('KHALEESI_SETTINGS')
    if not config_dir:
        raise ValueError("Missing path to configuration tree (settings dir)")

    config_dir = path.abspath(config_dir)

    if not path.exists(config_dir):
        raise ValueError("Bad path to configuration tree (settings dir): %s"
                         % config_dir)

    return config_dir


def main(args=None):
    args = args or sys.argv
    yaml_utils.register()

    # given a directory tree can you generate docstring?
    args = docopt(__doc__, options_first=True)
    _setup_logging(args['--log-level'])

    cmd = args['<command>']

    config_dir = get_config_dir(args)

    logging.debug("config_dir = %s" % config_dir)

    try:
        if cmd == 'help':
            return usage(config_dir)

        if cmd == 'generate':
            return settings.Generator(config_dir, args['<args>']).run()
    except settings.ArgsConflictError as exc:
        logging.error(str(exc))
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
