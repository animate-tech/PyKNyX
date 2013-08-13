#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Python KNX framework

License
=======

 - B{pKNyX} (U{http://www.pknyx.org}) is Copyright:
  - (C) 2013 Frédéric Mantegazza

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

Monitor tool to monitor all bus activity (multicast stuff only for now).

Implements
==========

 - B{MonitorGroupObject}

Documentation
=============

This script is used to send/receive multicast requests. It mimics what the stack does.

@todo: make the same using the stack.

Usage
=====


@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id: multicast.py 287 2013-08-07 07:17:28Z fma $"

import sys
import time
import argparse
import threading

from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger
from pknyx.core.dptXlator.dptXlatorFactory import DPTXlatorFactory
from pknyx.core.group import Group
from pknyx.core.groupListener import GroupListener
from pknyx.stack.stack import Stack
from pknyx.stack.priority import Priority


class MonitorGroupObject(GroupListener):
    """
    """
    def __init__(self):
        """ Init the group listener
        """
        super(SimpleGroupObject, self).__init__()

        self._responseQueue = SimpleQueue()

    def onWrite(self, src, data):
        Logger().debug("SimpleGroupObject.onWrite(): src=%s, data=%s" % (src, repr(data)))

    def onRead(self, src):
        Logger().debug("SimpleGroupObject.onRead(): src=%s" % src)

    def onResponse(self, src, data):
        Logger().debug("SimpleGroupObject.onResponse(): src=%s, data=%s" % (src, repr(data)))

        self._responseQueue.acquire()
        try:
            self._responseQueue.append(data)
            self._responseQueue.notify()
        finally:
            self._responseQueue.release()

    @property
    def responseQueue(self):
        return self._responseQueue


def write(gad, value, dptId="1.xxx", src="0.0.0",  priority="low", hopCount=6):
    """
    """
    if not isinstance(priority, Priority):
        priority = Priority(priority)

    stack = Stack(individualAddress=src)

    groupObject = SimpleGroupObject()
    group = stack.agds.subscribe(gad, groupObject)

    dptXlator = DPTXlatorFactory().create(dptId)
    type_ = type(dptXlator.dpt.limits[0])  # @todo: implement this in dptXlators
    value = type_(value)
    data = dptXlator.dataToFrame(dptXlator.valueToData(value))

    stack.start()
    try:
        group.write(priority, data, dptXlator.typeSize)
        time.sleep(1)  # Find a way to wait until the stack sending queue is empty (stack.waitEmpty()?)

    finally:
        stack.stop()


def read(gad, timeout=1, wait=True, dptId="1.xxx", src="0.0.0", priority="low", hopCount=6):
    """
    """
    if not isinstance(priority, Priority):
        priority = Priority(priority)

    stack = Stack(individualAddress=src)

    groupObject = SimpleGroupObject()
    group = stack.agds.subscribe(gad, groupObject)

    stack.start()
    try:
        group.read(priority)

        if wait:
            groupObject._responseQueue.acquire()
            try:
                groupObject._responseQueue.wait(timeout)  # Find a wait to know if timeout expired
                data = groupObject.responseQueue.pop()
            finally:
                groupObject._responseQueue.release()

            dptXlator = DPTXlatorFactory().create(dptId)
            value = dptXlator.dataToValue(dptXlator.frameToData(data))
            print "value =", value

    finally:
        stack.stop()


def response(gad, value, dptId="1.xxx", src="0.0.0",  priority="low", hopCount=6):
    """
    """
    if not isinstance(priority, Priority):
        priority = Priority(priority)

    stack = Stack(individualAddress=src)

    groupObject = SimpleGroupObject()
    group = stack.agds.subscribe(gad, groupObject)

    dptXlator = DPTXlatorFactory().create(dptId)
    type_ = type(dptXlator.dpt.limits[0])  # @todo: implement this in dptXlators
    value = type_(value)
    data = dptXlator.dataToFrame(dptXlator.valueToData(value))

    stack.start()
    try:
        group.response(priority, data, dptXlator.typeSize)
        time.sleep(1)  # Find a way to wait until the stack sending queue is empty (stack.waitEmpty()?)

    finally:
        stack.stop()


def monitor(dptId="1.xxx", src="0.0.0", priority="low", hopCount=6):
    """
    """
    stack = Stack(individualAddress=src)

    groupObject = MonitorGroupObject()
    group = stack.agds.subscribe("0/0/0", groupObject)
    #group = stack.agds.monitor(groupObject)

    stack.mainLoop()


def main():

    # Common options
    parser = argparse.ArgumentParser(prog="multicast",
                                     description="This tool is used to send multicast requests on KNX bus.",
                                     epilog="Under developement...")
    parser.add_argument("-l", "--logger",
                        choices=["trace", "debug", "info", "warning", "error", "exception", "critical"],
                        action="store", dest="debugLevel", default="warning", metavar="LEVEL",
                        help="logger level")
    parser.add_argument("-d", "--dptId", action="store", type=str, dest="dptId", default="1.xxx",
                        help="DPTID to use to encode/decode data")
    parser.add_argument("-s", "--srcAddr", action="store", type=str, dest="src", default="0.0.0",
                        help="source address to use")
    parser.add_argument("--priority", choices=["system", "normal", "urgent", "low"],
                        type=str, dest="priority", default="low",
                        help="bus priority")
    parser.add_argument("--hopCount", type=int, dest="hopCount", default=6, metavar="HOPCOUNT",
                        help="hopcount")

    # Create sub-parsers for write and read commands
    subparsers = parser.add_subparsers(title="subcommands", description="valid subcommands",
                                       help="sub-command help")

    # Write parser
    parserWrite = subparsers.add_parser("write",
                                        help="send a write request")
    parserWrite.set_defaults(func=write)
    parserWrite.add_argument("gad", type=str,
                             help="group address")
    parserWrite.add_argument("value", type=str,
                             help="value to send")

    # Read parser
    parserRead = subparsers.add_parser("read",
                                       help="send a read request")
    parserRead.set_defaults(func=read)
    parserRead.add_argument("-t", "--timeout", type=int, default=1, metavar="TIMEOUT",
                            help="read timeout")
    parserRead.add_argument("-n", "--no-wait", action="store_false", dest="wait", default=True,
                            help="wait for response")
    parserRead.add_argument("gad", type=str,
                            help="group address")

    # Response parser
    parserResponse = subparsers.add_parser("response",
                                        help="send a response indication")
    parserResponse.set_defaults(func=response)
    parserResponse.add_argument("gad", type=str,
                                help="group address")
    parserResponse.add_argument("value", type=str,
                                help="value to send")

    # Monitor parser
    monitorResponse = subparsers.add_parser("monitor",
                                        help="monitor bus")
    monitorResponse.set_defaults(func=monitor)

    # Parse
    args = parser.parse_args()

    Logger().setLevel(args.debugLevel)

    options = dict(vars(args))
    options.pop("debugLevel")
    options.pop("func")
    args.func(**options)


if __name__ == '__main__':
    main()