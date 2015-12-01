# This file is part of the esale_stock module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class EsaleStockTestCase(ModuleTestCase):
    'Test Esale Stock module'
    module = 'esale_stock'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        EsaleStockTestCase))
    return suite