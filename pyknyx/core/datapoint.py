# -*- coding: utf-8 -*-

""" Python KNX framework

License
=======

 - B{PyKNyX} (U{https://github.com/knxd/pyknyx}) is Copyright:
  - © 2016-2017 Matthias Urlichs
  - PyKNyX is a fork of pKNyX
   - © 2013-2015 Frédéric Mantegazza

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

Datapoint management

Implements
==========

 - B{Datapoint}
 - B{DatapointValueError}

Documentation
=============

Usage
=====

>>> from datapoint import Datapoint
>>> dp = Datapoint(None, id="test", name="PID_TEST", access='output')
>>> dp
<Datapoint(id='test', name='PID_TEST', access='output', dptId='1.xxx')>
>>> dp.id
'test'
>>> dp.name
'PID_TEST"
>>> dp.access
'output'
>>> dp.dptId
<DPTID("1.xxx")>

@author: Frédéric Mantegazza
@copyright: (C) 2013-2015 Frédéric Mantegazza
@license: GPL
"""

from pyknyx.common.exception import PyKNyXValueError
from pyknyx.services.logger import logging; logger = logging.getLogger(__name__)
from pyknyx.common.signal import Signal
from pyknyx.core.dptXlator.dptXlatorFactory import DPTXlatorFactory
from pyknyx.core.dptXlator.dpt import DPTID
from pyknyx.stack.flags import Flags
from pyknyx.stack.priority import Priority


class DatapointValueError(PyKNyXValueError):
    """
    """

class DP(object):
    """ Datapoint factory
        
    This class collects arguments for instantiating a L{Datapoint} when a
    L{FunctionalBlock} is created.

    Arguments are the same as L{Datapoint}, except that the B{obj} is
    missing – it does not exist yet.
    """ 

    def __init__(self, name=None, *args, **kwargs):
        """ Remember parameters for eventual instantiation of a L{Datapoint}.

        See B{Datapoint.__init__} for parameters (except for B{obj}).
        """
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def gen(self, obj, name=None):
        """ Instantiate the datapoint.

        If no name is passed in here, the one used in creating this object
        is used as a fallback.

        @param owner: owner of the datapoint.
        @type owner: L{FunctionalBlock<pyknyx.core.functionalBloc>}

        @param name: name of the datapoint. 
        @type name: str
        """
        if name is None:
            name = self.name
        assert name, "A Datapoint needs to be named"

        dp = Datapoint(obj, name, *self.args, **self.kwargs)
        dp._factory = self # required for finding it in GroupObject creation
        return dp

class Datapoint(object):
    """ Datapoint handling class

    The term B{data} refers to the KNX representation of the python type B{value}. It is stored in this object.
    The B{frame} is the 'data' as bytearray, which can be sent/received over the bus.

    @ivar _owner: owner of the Datapoint
    @type _owner: L{FunctionalBlock<pyknyx.core.functionalBlock>}

    @ivar _name: name of the Datapoint
    @type _name: str

    @ivar _access: access to Datapoint, in ('input', 'output', 'param') -> restrict read/write value?
                   - input:
                   - output:
                   - param:
    @type _access: str

    @ivar _dptId: Datapoint Type ID
    @type _dptId: str or L{DPTID}

    @ivar _default: value to use as default
    @type _default: depend on the DPT

    @ivar _data: KNX encoded data
    @type _data: depends on sub-class

    @ivar _dptXlator: DPT translator associated with this Datapoint
    @type _dptXlator: L{DPTXlator<pyknyx.core.dptXlator>}

    @ivar _dptXlatorGeneric: generic DPT translator associated with this Datapoint
    @type _dptXlatorGeneric: L{DPTXlator<pyknyx.core.dptXlator>}

    @ivar _flags: Flags used to auto-instantiate a GO
    @type _flags: L{Flags<pyknyx.stack.flags>}

    @ivar _priority: Priority used to auto-instantiate a GO, require Flags to be set
    @type _priority: L{Flags<pyknyx.stack.priority>}

    @ivar _signalChanged: emitted when the datapoint value has been updated by the owner
                          Used to notify associated GroupObject (and other proxies), if any
                          Params sent are datapoint name, old and new values.
    @type _signalChanged: L{Signal}

    @todo: add desc. param
    @todo: take 'access' into account when transmit/receive
    """
    def __init__(self, owner, name, access, dptId, default=None, flags=None, priority=None):
        """

        @param owner: owner of the datapoint
        @type owner: L{FunctionalBlock<pyknyx.core.functionalBloc>}

        @param name: name of the Datapoint
        @type name: str

        @param access: access to Datapoint, in ('input', 'output', 'param')
        @type access: str

        @param dptId: Datapoint Type ID
        @type dptId: str or L{DPTID}

        @param default: value to use as default
        @type default: depend on the DPT

        @param flags: Flags to auto-instantiate a GO
        @type flags: Flags
        """
        super(Datapoint, self).__init__()

        #logger.debug("Datapoint.__init__(): name=%s, access=%s, dptId=%s, default=%s" % \
                       #repr(name), repr(access), repr(dptId), repr(default)))

        # Check input
        if access not in ('input', 'output', 'param'):
            raise DatapointValueError("invalid access (%s)" % repr(access))

        self._owner = owner
        self._name = name
        if not isinstance(dptId, DPTID):
            dptId = DPTID(dptId)
        self._dptId = dptId
        self._access = access
        self._default = default
        self._data = None
        self._flags = None if flags is None else Flags(flags)
        self._priority = None if priority is None else Priority(priority)

        self._dptXlator = DPTXlatorFactory().create(dptId)
        if dptId != dptId.generic:
            self._dptXlatorGeneric = DPTXlatorFactory().create(dptId.generic)
        else:
            self._dptXlatorGeneric = self._dptXlator

        # Signals definition
        self._signalChanged = Signal()

        # Set default value
        if default is not None:
            self._setValue(default)

    def __repr__(self):
        return "<Datapoint(name='%s', access='%s', dptId='%s')>" % \
               (self._name, self._access, self._dptId)

    def __str__(self):
        return "<Datapoint('%s')>" % self._name

    @property
    def owner(self):
        return self._owner

    @property
    def name(self):
        return self._name

    @property
    def dptId(self):
        return self._dptId

    @property
    def flags(self):
        return self._flags

    @property
    def priority(self):
        return self._priority

    @property
    def access(self):
        return self._access

    @property
    def default(self):
        return self._default

    @property
    def data(self):
        return self._data

    def _setData(self, data):
        self._dptXlator.checkData(data)
        self._data = data

    @property
    def dptXlator(self):
        return self._dptXlator

    @property
    def dptXlatorGeneric(self):
        return self._dptXlatorGeneric

    @property
    def signalChanged(self):
        return self._signalChanged

    @property
    def value(self):
        if self._data is None:
            return None
        return self._dptXlator.dataToValue(self._data)

    def _setValue(self, value):
        self._dptXlator.checkValue(value)
        data = self._dptXlator.valueToData(value)
        self._setData(data)
        # @todo: check access

    @value.setter
    def value(self, value):
        oldValue = self.value
        self._dptXlator.checkValue(value)
        data = self._dptXlator.valueToData(value)
        self._setData(data)
        # @todo: check access

        # Notify associated GroupObject (if any)
        self._signalChanged.emit(oldValue=oldValue, newValue=self.value)

        # Notify owner (FunctionalBlock)
        self._owner.notify(self, oldValue, self.value)  # TBD

    @property
    def unit(self):
        return self._dptXlator.unit

    @property
    def frame(self):
        return (self._dptXlator.dataToFrame(self._data), self._dptXlator.typeSize)

    @frame.setter
    def frame(self, frame):
        oldValue = self.value
        data = self._dptXlator.frameToData(frame)  # @todo: check frame size with _dptXlator.typeSize...
        self._setData(data)

        # Notify owner (FunctionalBlock)
        self._owner.notify(self, oldValue, self.value)

