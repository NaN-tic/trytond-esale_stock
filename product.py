#This file is part esale_stock module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['Template']
__metaclass__ = PoolMeta


class Template:
    "Product Template"
    __name__ = 'product.template'
    esale_manage_stock = fields.Boolean('Manage Stock',
            help='Manage stock in e-commerce')

    @staticmethod
    def default_esale_manage_stock():
        return True
