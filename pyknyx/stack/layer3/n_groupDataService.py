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

Network layer group data management

Implements
==========

 - B{N_GroupDataService}

Documentation
=============

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013-2015 Frédéric Mantegazza
@license: GPL
"""


from pyknyx.common.exception import PyKNyXValueError
from pyknyx.services.logger import logging; logger = logging.getLogger(__name__)
from pyknyx.stack.groupAddress import GroupAddress
from pyknyx.stack.individualAddress import IndividualAddress
from pyknyx.stack.layer2.l_dataListener import L_DataListener
from pyknyx.stack.cemi.cemiLData import CEMILData, CEMIValueError


class N_GDSValueError(PyKNyXValueError):
    """
    """


class N_GroupDataService(L_DataListener):
    """ N_GroupDataService class

    @ivar _lds: link data service object
    @type _lds: L{L_DataService<pyknyx.core.layer2.l_dataService>}

    @ivar _ngdl: network group data listener
    @type _ngdl: L{N_GroupDataListener<pyknyx.core.layer3.n_groupDataListener>}
    """
    def __init__(self, lds, hopCount=6):
        """

        @param lds: Link data service object
        @type lds: L{L_DataService<pyknyx.core.layer2.l_dataService>}

        raise N_GDSValueError:
        """
        super(N_GroupDataService, self).__init__()

        self._lds = lds

        self._ngdl = None
        if not 0 < hopCount < 7:
            raise N_GDSValueError("invalid hopCount (%d)" % hopCount)
        self._hopCount = hopCount

        lds.setListener(self)

    def dataInd(self, cEMI):
        logger.debug("N_GroupDataService.dataInd(): cEMI=%s" % repr(cEMI))

        if self._ngdl is None:
            logger.warning("N_GroupDataService.dataInd(): not listener defined")
            return

        hopCount = cEMI.hopCount
        mc = cEMI.messageCode
        src = cEMI.sourceAddress
        dest = cEMI.destinationAddress
        priority = cEMI.priority
        hopCount = cEMI.hopCount
        nSDU = cEMI.npdu[1:]

        if isinstance(dest, GroupAddress):
            if not dest.isNull:
                self._ngdl.groupDataInd(src, dest, priority, nSDU)
            #else:
                #self._ngdl.broadcastInd(src, priority, hopCount, nSDU)
        #elif isinstance(dest, IndividualAddress):
            #self._ngdl.dataInd(src, priority, hopCount, nSDU)
        #else:
            #logger.warning("N_GroupDataService.dataInd(): unknown destination address type (%s)" % repr(dest))
        else:
            logger.warning("N_GroupDataService.dataInd(): unsupported destination address type (%s)" % repr(dest))

    def setListener(self, ngdl):
        """

        @param ngdl: listener to use to transmit data
        @type ngdl: L{N_GroupDataListener<pyknyx.core.layer3.n_groupDataListener>}
        """
        self._ngdl = ngdl

    def groupDataReq(self, gad, priority, nSDU):
        """
        """
        logger.debug("N_GroupDataService.groupDataReq(): gad=%s, priority=%s, nSDU=%s" % \
                       (gad, priority, repr(nSDU)))

        if gad.isNull:
            raise N_GDSValueError("invalid Group Address")

        cEMI = CEMILData()
        cEMI.messageCode = CEMILData.MC_LDATA_IND  # ???!!!??? Does not work with MC_LDATA_REQ!!!
        #cEMI.sourceAddress = src  # Added by Link Data Layer
        cEMI.destinationAddress = gad
        cEMI.priority = priority
        cEMI.hopCount = self._hopCount
        nPDU = bytearray(len(nSDU) + 1)
        nPDU[0] = len(nSDU) - 1
        nPDU[1:] = nSDU
        cEMI.npdu = nPDU

        return self._lds.dataReq(cEMI)

