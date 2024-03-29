import logging
from logging.handlers import RotatingFileHandler
from systemd import journal
from os.path import exists

file_log_info = 'log/relay-controller.log'
file_log_error = 'log/relay-controller.err'

if exists(file_log_info):
    with open(file_log_info, "w+"):
        pass

if exists(file_log_error):
    with open(file_log_error, "w+"):
        pass

# create logger with 'Relay-Controller'
logger = logging.getLogger('Relay-Controller')
logger.setLevel(logging.DEBUG)
logger.propagate = False  # Fixes double log to journal

# create file handler which logs even debug messages
ih = RotatingFileHandler(filename=file_log_info, backupCount=1, maxBytes=5 * 1024 * 1024)
ih.setLevel(logging.DEBUG)

# create file handler with a higher log level
eh = RotatingFileHandler(filename=file_log_error, backupCount=1, maxBytes=5 * 1024 * 1024)
eh.setLevel(logging.ERROR)

# create journal handler
# jh = logging.StreamHandler()
jh = journal.JournalHandler()
jh.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ih.setFormatter(formatter)
eh.setFormatter(formatter)
jh.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

# add the handlers to the logger
logger.addHandler(ih)
logger.addHandler(eh)
logger.addHandler(jh)
