# -*- coding: utf-8 -*-

""" Python KNX framework.

License
=======

 - B{pKNyX} (U{http://www.pknyx.org}) is Copyright:
  - (C) 2013-2015 Frédéric Mantegazza

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
or see:

 - U{http://www.gnu.org/licenses/gpl.html}

Module purpose
==============

Logging service

Implements
==========

- B{LoggerValueError}
- B{LoggerObject}

@author: Frédéric Mantegazza
@copyright: (C) 2013-2015 Frédéric Mantegazza
@license: GPL
"""

import logging
import logging.handlers
try:
    from io import StringIO
except ImportError:
    import StringIO
import traceback
import os.path
import time

from pknyx.common import config
from pknyx.common.exception import PKNyXValueError
from pknyx.common.singleton import Singleton
from pknyx.services.loggerFormatter import DefaultFormatter, ColorFormatter, \
                                           SpaceFormatter, SpaceColorFormatter

LEVELS = {'trace': logging.DEBUG - 5,
          'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'exception': logging.ERROR + 5,
          'critical': logging.CRITICAL}


class LoggerValueError(PKNyXValueError):
    """
    """


class Logger(object):
    """ Logger object.
    """
    __metaclass__ = Singleton

    def __init__(self, deviceName=None):
        """ Init object.

        @param deviceName: name of the file used by the file handler
        @type deviceName: str
        """
        super(Logger, self).__init__()

        logging.TRACE = LEVELS['trace']
        logging.EXCEPTION = LEVELS['exception']
        logging.raiseExceptions = 0
        logging.addLevelName(logging.TRACE, "TRACE")
        logging.addLevelName(logging.EXCEPTION, "EXCEPTION")

        # Logger
        self._logger = logging.getLogger(config.APP_NAME)
        self._logger.propagate = False

        # Handlers
        self._stdoutStreamHandler = logging.StreamHandler()
        streamFormatter = SpaceColorFormatter(config.LOGGER_STREAM_FORMAT)
        self._stdoutStreamHandler.setFormatter(streamFormatter)
        self._logger.addHandler(self._stdoutStreamHandler)

        if config.LOGGER_BACKUP_COUNT:
            loggerFilename = os.path.join(config.LOGGER_DIR, "%s_%s.log" % (config.APP_NAME, deviceName))
            fileHandler = logging.handlers.RotatingFileHandler(loggerFilename, 'w',
                                                               config.LOGGER_MAX_BYTES,
                                                               config.LOGGER_BACKUP_COUNT)
            fileFormatter = SpaceFormatter(config.LOGGER_FILE_FORMAT)
            fileHandler.setFormatter(fileFormatter)
            self._logger.addHandler(fileHandler)

        self.setLevel(config.LOGGER_LEVEL)

    def addStreamHandler(self, stream, formatter=DefaultFormatter):
        """ Add a new stream handler.

        Can be used to register a new GUI handler.

        @param stream: open stream where to write logs
        @type stream: file

        @param formatter: associated formatter
        @type formatter: L{DefaultFormatter<pknyx.services.loggingFormatter>}
        """
        handler = logging.StreamHandler(stream)
        handler.setFormatter(formatter(config.LOGGER_FORMAT))
        self._logger.addHandler(handler)

    def setLevel(self, level):
        """ Change logging level.

        @param level: new level, in ('trace', 'debug', 'info', 'warning', 'error', 'exception', 'critical')
        @type level: str
        """
        if level not in LEVELS.keys():
            raise LoggerValueError("Logger level must be in %s" % LEVELS.keys())
        self._logger.setLevel(LEVELS[level])

        if self._logger.level >= logging.INFO:
            streamFormatter = SpaceColorFormatter("")
        else:
            streamFormatter = SpaceColorFormatter(config.LOGGER_STREAM_FORMAT)
        self._stdoutStreamHandler.setFormatter(streamFormatter)

    def trace(self, message, *args, **kwargs):
        """ Logs a message with level TRACE.

        @param message: message to log
        @type message: string
        """
        self._logger.log(logging.TRACE, message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        """ Logs a message with level DEBUG.

        @param message: message to log
        @type message: string
        """
        self._logger.debug(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        """ Logs a message with level INFO.

        @param message: message to log
        @type message: string
        """
        self._logger.info(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        """ Logs a message with level WARNING.

        @param message: message to log
        @type message: string
        """
        self._logger.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        """ Logs a message with level ERROR.

        @param message: message to log
        @type message: string
        """
        self._logger.error(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        """ Logs a message with level CRITICAL.

        @param message: message to log
        @type message: string
        """
        self._logger.critical(message, *args, **kwargs)

    def exception(self, message, debug=False, *args, **kwargs):
        """ Logs a message within an exception.

        @param message: message to log
        @type message: string

        @param debug: flag to log exception on DEBUG level instead of EXCEPTION one
        @type debug: bool
        """
        kwargs['exc_info'] = True
        if debug:
            self.debug(message, *args, **kwargs)
        else:
            self.log(logging.EXCEPTION, message, *args, **kwargs)

    def log(self, level, message, *args, **kwargs):
        """ Logs a message with given level.

        @param level: log level to use
        @type level: int or str

        @param message: message to log
        @type message: string
        """
        if isinstance(level, str):
            level = LEVELS[level]
        self._logger.log(level, message, *args, **kwargs)

    def getTraceback(self):
        """ Return the complete traceback.

        Should be called in an except statement.
        """
        tracebackString = StringIO.StringIO()
        traceback.print_exc(file=tracebackString)
        message = tracebackString.getvalue().strip()
        tracebackString.close()
        return message

    def shutdown(self):
        """ Shutdown the logging service.
        """
        logging.shutdown()
