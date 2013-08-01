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

Transport layer group data management

Implements
==========

 - B{T_GroupDataService}

Documentation
=============

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger
from pknyx.stack.layer3.n_groupDataListener import N_GroupDataListener
from pknyx.stack.transceiver.tFrame import TFrame


class T_GDSValueError(PKNyXValueError):
    """
    """


class T_GroupDataService(N_GroupDataListener):
    """ T_GroupDataService class

    @ivar _ngds: network group data service object
    @type _ngds: L{N_GroupDataService<pknyx.core.layer3.n_groupDataService>}

    @ivar _tgdl: transport group data listener
    @type _tgdl: L{T_GroupDataListener<pknyx.core.layer4.t_groupDataListener>}
    """
    UNNUMBERED_DATA = 0x00
    NUMBERED_DATA   = 0x40
    #CONNECT_REQ     = 0x80
    #CONNECT_CON     = 0x82
    #DISCONNECT_REQ  = 0x81
    #DATA_ACK        = 0xc2
    #DATA_NACK       = 0xc3

    def __init__(self, ngds):
        """

        @param ngds: Network group data service object
        @type ngds: L{L_GroupDataService<pknyx.core.layer3.n_groupDataService>}

        raise T_GDSValueError:
        """
        super(T_GroupDataService, self).__init__()

        self._ngds = ngds

        self._tgdl = None

        ngds.setListener(self)

    #def _setTPCI(self, tPDU, packetType, seqNo):
        #""" Generate the TPCI

        #@param tPDU: Transport Packet Data Unit
        #@type tPDU: bytearray

        #@param packetType:
        #@type packetType:

        #@param seqNo:
        #@type seqNo:

        #@todo: create a TPDU object, and move this method there
        #"""
        #if packetType in (T_GroupDataService.UNNUMBERED_DATA, T_GroupDataService.NUMBERED_DATA):
            #tPDU[TFrame.TPCI_BYTE] = (tPDU[TFrame.TPCI_BYTE] & 0x03) | packetType | (seqNo << 2)
        #else:
            #tPDU[TFrame.TPCI_BYTE] = packetType | (seqNo << 2)

    #def _getPacketType(self, tPDU):
        #""" Extract packet type fro given tPDU

        #@param tPDU: Transport Packet Data Unit
        #@type tPDU: bytearray

        #@todo: create a TPDU object, and move this method there
        #"""
        #packetType = tPDU[TFrame.TPCI_BYTE] & 0xc0
        #if packetType not in (T_GroupDataService.UNNUMBERED_DATA, T_GroupDataService.NUMBERED_DATA):
            #packetType = tPDU[TFrame.TPCI_BYTE] & 0xc3
        #return packetType

    def groupDataInd(self, src, gad, priority, tPDU):
        Logger().debug("T_GroupDataService.groupDataInd(): src=%s, gad=%s, priority=%s, tPDU=%s" % \
                       (src, gad, priority, repr(tPDU)))

        if self._tgdl is None:
            Logger().warning("T_GroupDataService.groupDataInd(): not listener defined")
            return

        #if self._getPacketType(tPDU) == T_GroupDataService.UNNUMBERED_DATA:
        tPCI = tPDU[0] & 0xc0
        if tPCI == T_GroupDataService.UNNUMBERED_DATA:
            tSDU = tPDU
            tSDU[0] &= 0x3f
            self._tgdl.groupDataInd(src, gad, priority, tSDU)

    def setListener(self, tgdl):
        """

        @param tgdl: listener to use to transmit data
        @type tgdl: L{T_GroupDataListener<pknyx.core.layer4.t_groupDataListener>}
        """
        self._tgdl = tgdl

    def groupDataReq(self, gad, priority, tSDU):
        """
        """
        Logger().debug("T_GroupDataService.groupDataReq(): gad=%s, priority=%s, tSDU=%s" % \
                       (gad, priority, repr(tSDU)))

        #self._setTPCI(tSDU, T_GroupDataService.UNNUMBERED_DATA, 0)
        tPDU = tSDU
        tPDU[0] |= T_GroupDataService.UNNUMBERED_DATA
        return self._ngds.groupDataReq(gad, priority, tPDU)


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class T_GDSTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_constructor(self):
            pass


    unittest.main()
