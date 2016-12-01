# This file is part esale_stock module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from .product import *
from .shop import *


def register():
    Pool.register(
        EsaleExportStockStart,
        EsaleExportStockResult,
        EsaleExportStockCSVStart,
        EsaleExportStockCSVResult,
        Template,
        Product,
        SaleShop,
        module='esale_stock', type_='model')
    Pool.register(
        EsaleExportStock,
        EsaleExportStockCSV,
        module='esale_stock', type_='wizard')
