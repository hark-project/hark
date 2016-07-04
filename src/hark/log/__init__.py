import logging
import os
import tempfile

fileFormatter = logging.Formatter('%(asctime)s | %(levelname)s: %(message)s')
streamFormatter = logging.Formatter('%(levelname)s: %(message)s')

# Set the level on the root handler to the most verbose possible level
logging.getLogger().setLevel(logging.DEBUG)

# Get the main handler for our app
logger = logging.getLogger('hark')

# Create the stream handler, whose level is changed by setLevel() calls, and
# add it to the main handler. It logs to sys.stderr.
streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.DEBUG)
streamHandler.setFormatter(streamFormatter)
logger.addHandler(streamHandler)

_tempLogFile = tempfile.mktemp()
tempFileHandler = logging.FileHandler(
    _tempLogFile, delay=True)
tempFileHandler.setLevel(logging.DEBUG)
tempFileHandler.setFormatter(fileFormatter)
logger.addHandler(tempFileHandler)


def setLevel(level):
    streamHandler.setLevel(level.upper())


def setOutputFile(filename):
    "Set the output file for log messages"

    if not os.path.exists(filename):
        info("Creating hark log file: %s", filename)

    # There is an awkward bootstrapping problem to work around here: before the
    # hark CLI can set the output file, it has to actually create it, and we
    # want log of the steps it has to has to take before creating it.
    #
    # This is solved by having a FileHandler set up above that writes to a
    # temporary file. When setOutputFile is called, we write all messages from
    # the temporary file it created into the real file.
    global tempFileHandler

    if tempFileHandler is not None and os.path.exists(_tempLogFile):
        debug(
            "log bootstrapping complete: copying %s into %s",
            _tempLogFile, filename)
        tempFileHandler.close()

        with open(_tempLogFile, 'r') as f:
            with open(filename, 'a') as newF:
                for i, line in enumerate(f):
                    newF.write(line)

        tempFileHandler = None
        os.remove(_tempLogFile)

    fileHandler = logging.FileHandler(filename, delay=True)
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(fileFormatter)
    logger.addHandler(fileHandler)


def debug(msg, *args):
    logger.debug(msg, *args)


def info(msg, *args):
    logger.info(msg, *args)


def error(msg, *args):
    logger.error(msg, *args)
