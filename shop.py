#This file is part esale_stock module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

import datetime

__all__ = ['SaleShop']
__metaclass__ = PoolMeta


class SaleShop:
    __name__ = 'sale.shop'
    esale_last_stocks = fields.DateTime('Last Stocks', 
        help='This date is last export (filter)')

    @classmethod
    def __setup__(cls):
        super(SaleShop, cls).__setup__()
        cls._error_messages.update({
            'stock_not_export': 'Threre are not stock method to export',
            'select_date_stocks': 'Select a date to export stocks',
        })
        cls._buttons.update({
                'export_stocks': {},
                })

    @classmethod
    def get_product_from_move_and_date(self, shop, date):
        '''Get Products from a move and date to export
        :param shop: obj
        :param date: datetime
        retun list
        '''
        pool = Pool()
        Move = pool.get('stock.move')
        Product = pool.get('product.product')

        # Get all moves from date and filter products by shop
        moves = Move.search(['OR', [
            ('shipment', 'like', 'stock.shipment.out%'),
            ('shipment', 'like', 'stock.shipment.in%'),
        ], [
            ('write_date', '>=', date),
        ]])

        products = Product.search([
            ('id', 'in', map(int, [m.product.id for m in moves])),
            ])
        products_to_export = [product for product in products 
                if shop in product.template.esale_saleshops]
        return products_to_export

    def get_esale_product_quantity(self, products):
        '''
        Get product forecast quantity from all storage locations
        :param products: obj list
        return dict
        '''
        pool = Pool()
        Location = pool.get('stock.location')
        Product = pool.get('product.product')

        locations = Location.search([
                ('type', '=', 'storage'),
                ])

        context = {}
        context['locations'] = [l.id for l in locations]
        with Transaction().set_context(context):
            quantities = Product.get_quantity(products, name='forecast_quantity')
        return quantities

    @classmethod
    @ModelView.button
    def export_stocks(self, shops):
        """
        Export Stocks to External APP
        """
        for shop in shops:
            if not shop.esale_last_stocks:
                self.raise_user_error('select_date_stocks')
            export_stocks = getattr(shop, 'export_stocks_%s' % shop.esale_shop_app)
            export_stocks(shop)

    @classmethod
    def export_cron_stock(cls):
        """
        Cron export stock:
        """
        shops = cls.search([
            ('esale_available', '=', True),
            ('esale_scheduler', '=', True),
            ])
        cls.export_stocks(shops)
        return True
