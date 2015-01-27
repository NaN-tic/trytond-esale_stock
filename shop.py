# This file is part esale_stock module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

__all__ = ['SaleShop']
__metaclass__ = PoolMeta


class SaleShop:
    __name__ = 'sale.shop'
    esale_last_stocks = fields.DateTime('Last Stocks',
        help='This date is last export (filter)')
    esale_forecast_quantity = fields.Boolean('Forecast Quantity')

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

    @staticmethod
    def default_esale_forecast_quantity():
        return True

    def get_product_from_move_and_date(self, date):
        '''Get Products from a move and date to export
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
                if self in product.template.esale_saleshops]
        return products_to_export

    def get_esale_product_quantity(self, products):
        '''
        Get product forecast quantity from all storage locations
        :param products: obj list
        return dict
        '''
        pool = Pool()
        Product = pool.get('product.product')
        if not self.esale_forecast_quantity:
            return Product.get_quantity(products, 'forecast_quantity')
        return Product.get_esale_quantity(products, 'esale_forecast_quantity')

    @classmethod
    @ModelView.button
    def export_stocks(cls, shops):
        """
        Export Stocks to External APP
        """
        for shop in shops:
            if not shop.esale_last_stocks:
                cls.raise_user_error('select_date_stocks')
            export_stocks = getattr(shop,
                'export_stocks_%s' % shop.esale_shop_app)
            export_stocks()

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
