# -*- coding: utf-8 -*-

from pyknyx.stack.stack import *
import unittest

# Mute logger
from pyknyx.services.logger import logging
logger = logging.getLogger(__name__)
logging.getLogger("pyknyx").setLevel(logging.ERROR)


class StackTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_constructor(self):
        pass

