# -*- coding: utf-8 -*-

""" Python KNX framework

pKNyX is high level KNX framework written entirely in python. It goal is to build
in a very simple and efficient way applications to extend capabilities of a
KNX installation, by adding rules and/or virtual devices, and thus create a smart
processor for KNX home automation.

This project is moslty a (partial) port of the great java library, Calimero, but
add high level tools to be more user-friendly.

It is also inspired from the following projects:

 - linknx
 - eibd
 - eibnetmux
 - PywireGate
 - OpenHAB

The main target of pKNyX is an ALIX board running OpenWRT, but can run on any system
when python is available. It does not require any compilation.

For more informations, see pKNyx web site et U{http://www.pknyx.org}

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

Datapoint Types management

Implements
==========

 - B{DPTValueError}
 - B{DPT}

Documentation
=============

From KNX documentation::

                    Datapoint Type
                          |
            ----------------------------
            |                           |
        Data Type                   Dimension
            |                           |
       -----------                 ----------
      |           |               |          |
   Format      Encoding         Range       Unit

The Datapoint Types are defined as a combination of a data type and a dimension. It has been preferred not to define the
data types separately from any dimension. This only leads to more abstract naming and identifications.

Any Datapoint Type thus standardizes one combination of format, encoding, range and unit. The Datapoint Types will be
used to describe further KNX Interworking Standards.

The Datapoint Types are identified by a 16 bit main number separated by a dot from a 16-bit subnumber, e.g. "7.002".
The coding is as follows::

    ---------------------------------------
     Field              | Stands for
    --------------------+------------------
     main number (left) | Format, Encoding
     subnumber (right)  | Range, Unit
    ---------------------------------------

Datapoint Types with the same main number thus have the same format and encoding.

Datapoint Types with the same main number have the same data type. A different subnumber indicates a different dimension
(different range and/or different unit).

Usage
=====

>>> from dpt import DPT
>>> dpt = DPT("1.001", "Switch", ("Off", "On"))
>>> dpt
<DPT(id="<DPTID("1.001")>", desc="Switch", limits=('Off', 'On'))>
>>> dpt.id
<DPTID("1.001")>
>>> dpt.id.main
'1'
>>> dpt.id.generic
<DPTID("1.xxx")>
>>> dpt.desc
'Switch'
>>> dpt.limits
('Off', 'On')

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

from pknyx.common.exception import PKNyXValueError
from pknyx.common.loggingServices import Logger
from pknyx.core.dpt.dptId import DPTID


class DPTValueError(PKNyXValueError):
    """
    """


class DPT(object):
    """ Datapoint Type hanlding class

    Manage Datapoint Type informations and behavior.

    @ivar _id: Datapoint Type ID
    @type _id: L{DPTID}

    @ivar _desc: description of the DPT
    @type _desc: str

    @ivar _limits: value limits the DPT can handle
    @type _limits: tuple of int/float/str

    @ivar _unit: optional unit of the DPT
    @type _unit: str
    """
    def __init__(self, dptId, desc, limits, unit=None):
        """ Init the DPT object

        @param dptId: available implemented Datapoint Type ID
        @type dptId: L{DPTID} or str

        @param desc: description of the DPT
        @type desc: str

        @param limits: value limits the DPT can handle
        @type limits: tuple of int/float/str

        @param unit: optional unit of the DPT
        @type unit: str

        @raise DPTValueError:
        """
        super(DPT, self).__init__()

        #Logger().debug("DPT.__init__(): id=%s, desc=%s, limits=%r, unit=%s" % (dptId, desc, limits, unit))

        if not isinstance(dptId, DPTID):
            dptId = DPTID(dptId)
        self._id = dptId
        self._desc = desc
        try:
            self._limits = tuple(limits)
        except TypeError:
            Logger().exception("DPT.__init__()", debug=True)
            raise DPTValueError("invalid limits")
        self._unit = unit

    def __repr__(self):
        if self._unit is not None:
            s = "<DPT(id=\"%r\", desc=\"%s\", limits=%s, unit=\"%s\")>" % (self._id, self._desc, repr(self._limits), self._unit)
        else:
            s = "<DPT(id=\"%r\", desc=\"%s\", limits=%s)>" % (self._id, self._desc, repr(self._limits))
        return s

    @property
    def id(self):
        """ return the DPT ID
        """
        return self._id

    @property
    def desc(self):
        """ return the DPT description
        """
        return self._desc

    @property
    def limits(self):
        """ return the DPT limits
        """
        return self._limits

    @property
    def unit(self):
        """ return the DPT unit
        """
        return self._unit


if __name__ == '__main__':
    import unittest


    class DPTTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_constructor(self):
            with self.assertRaises(DPTValueError):
                DPT("9.001", "Temperature", -273)


    unittest.main()
