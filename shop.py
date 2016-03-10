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
    esale_forecast_quantity = fields.Boolean('Forecast Quantity',
        help='Product stock is Forecast Quantity. If is dissabled, ' \
            'product stock is Quantity')

    @classmethod
    def __setup__(cls):
        super(SaleShop, cls).__setup__()
        cls._error_messages.update({
            'stock_not_export': 'Threre are not stock to export',
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
        cursor = Transaction().connection.cursor()
        pool = Pool()
        Move = pool.get('stock.move')
        Product = pool.get('product.product')
        Template = pool.get('product.template')
        TemplateShop = pool.get('product.template-sale.shop')

        # Get all moves from date and filter products by shop
        move = Move.__table__()
        product = Product.__table__()
        template = Template.__table__()
        template_shop = TemplateShop.__table__()

        cursor.execute(*move
            .join(product,
                condition=move.product == product.id)
            .join(template,
                condition=product.template == template.id)
            .join(template_shop,
                condition=template_shop.template == template.id)
            .select(product.id,
                where=(template.esale_available)
                    & (template.esale_active)
                    & (move.state.in_(('assigned', 'done')))
                    & (template_shop.shop == self.id)
                    & ((move.write_date >= date) | (move.create_date >= date)),
                group_by=product.id))
        return Product.browse([p[0] for p in cursor.fetchall()])

    def get_esale_product_quantity(self, products):
        '''
        Get product forecast quantity from all storage locations
        :param products: obj list
        return dict
        '''
        Product = Pool().get('product.product')
        if self.esale_forecast_quantity:
            return Product.get_esale_quantity(products, 'esale_forecast_quantity')
        return Product.get_esale_quantity(products, 'esale_quantity')

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

    def export_stocks_tryton(self, shop):
        """Export Stocks to Tryton e-Sale
        :param shop: Obj
        """
        self.raise_user_error('stock_not_export')
