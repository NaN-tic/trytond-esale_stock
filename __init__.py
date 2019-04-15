# This file is part esale_stock module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import product
from . import shop
from . import esale


def register():
    Pool.register(
        esale.Cron,
        product.EsaleExportStockStart,
        product.EsaleExportStockResult,
        product.EsaleExportStockCSVStart,
        product.EsaleExportStockCSVResult,
        product.Template,
        product.Product,
        shop.SaleShop,
        module='esale_stock', type_='model')
    Pool.register(
        product.EsaleExportStock,
        product.EsaleExportStockCSV,
        module='esale_stock', type_='wizard')
