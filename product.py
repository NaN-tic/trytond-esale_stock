# This file is part esale_stock module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import datetime
from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.transaction import Transaction
from trytond.pyson import Eval
from trytond.modules.product_esale.tools import slugify

__all__ = ['Template', 'Product', 'EsaleExportStockStart', 'EsaleExportStockResult',
    'EsaleExportStock', 'EsaleExportStockCSVStart', 'EsaleExportStockCSVResult',
    'EsaleExportStockCSV']


class Template:
    __metaclass__ = PoolMeta
    __name__ = 'product.template'
    esale_manage_stock = fields.Boolean('Manage Stock',
            help='Manage stock in e-commerce')

    @staticmethod
    def default_esale_manage_stock():
        return True


class Product:
    __metaclass__ = PoolMeta
    __name__ = 'product.product'

    @classmethod
    def esale_export_stock_csv(cls, shop, from_date):
        'eSale Export Stock CSV'
        products = shop.get_product_from_move_and_date(from_date)

        product_domain = getattr(cls, '%s_product_domain' % shop.esale_shop_app)
        domain = product_domain([shop.id])
        domain += [['OR',
                    ('create_date', '>=', from_date),
                    ('write_date', '>=', from_date),
                    ('template.create_date', '>=', from_date),
                    ('template.write_date', '>=', from_date),
                    ('id', 'in', [p.id for p in products]),
                ]]

        products = cls.search(domain)

        export_csv = getattr(shop, 'esale_export_stock_csv_%s' % shop.esale_shop_app)
        output = export_csv(products)
        return output


class EsaleExportStockStart(ModelView):
    'Export Tryton to External Shop: Start'
    __name__ = 'esale.export.stock.start'
    shops = fields.One2Many('sale.shop', None, 'Shops')
    shop = fields.Many2One('sale.shop', 'Shop', required=True,
        domain=[
            ('id', 'in', Eval('shops'))
        ], depends=['shops'],
        help='Select shop will be export this product.')


class EsaleExportStockResult(ModelView):
    'Export Tryton to External Shop: Result'
    __name__ = 'esale.export.stock.result'
    info = fields.Text('Info', readonly=True)


class EsaleExportStock(Wizard):
    """Export Stocks Tryton to External Shop"""
    __name__ = "esale.export.stock"

    start = StateView('esale.export.stock.start',
        'esale_stock.esale_export_stock_start', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Export', 'export', 'tryton-ok', default=True),
            ])
    export = StateTransition()
    result = StateView('esale.export.stock.result',
        'esale_stock.esale_export_stock_result', [
            Button('Close', 'end', 'tryton-close'),
            ])

    @classmethod
    def __setup__(cls):
        super(EsaleExportStock, cls).__setup__()
        cls._error_messages.update({
                'export_info': 'Export product stocks %s IDs to %s shop',
                'install_stock_sync': 'Install stock sync module to %s shop',
                })

    def default_start(self, fields):
        Template = Pool().get('product.template')
        templates = Template.browse(Transaction().context['active_ids'])
        shops = [s.id for t in templates for s in t.shops
            if s.esale_available]
        if not shops:
            return {}
        return {
            'shops': shops,
            'shop': shops[0],
            }

    def transition_export(self):
        shop = self.start.shop
        if hasattr(shop, 'export_stocks_%s' % shop.esale_shop_app):
            export_status = getattr(shop, 'export_stocks_%s' % shop.esale_shop_app)
            templates = Transaction().context['active_ids']
            export_status(templates)
            self.result.info = self.raise_user_error('export_info',
                    (','.join(str(t) for t in templates), shop.rec_name),
                    raise_exception=False)
        else:
            self.result.info = self.raise_user_error('install_stock_sync',
                    (shop.rec_name), raise_exception=False)
        return 'result'

    def default_result(self, fields):
        info_ = self.result.info
        return {
            'info': info_,
            }


class EsaleExportStockCSVStart(ModelView):
    'eSale Export Stock CSV Start'
    __name__ = 'esale.export.stock.csv.start'
    shop = fields.Many2One('sale.shop', 'Shop', required=True,
        domain=[('esale_available', '=', True)])
    from_date = fields.DateTime('From Date', required=True,
        help='Filter moves create/write from this date. '
        'An empty value are all catalog product.')

    @staticmethod
    def default_shop():
        User = Pool().get('res.user')
        user = User(Transaction().user)
        return user.shop.id if user.shop else None

    @staticmethod
    def default_from_date():
        return datetime.datetime.now()


class EsaleExportStockCSVResult(ModelView):
    'eSale Export Stock CSV Result'
    __name__ = 'esale.export.stock.csv.result'
    csv_file = fields.Binary('CSV', filename='file_name')
    file_name = fields.Text('File Name')


class EsaleExportStockCSV(Wizard):
    'eSale Export Stock CSV'
    __name__ = "esale.export.stock.csv"
    start = StateView('esale.export.stock.csv.start',
        'esale_stock.esale_export_stock_csv_start', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Export', 'export', 'tryton-ok', default=True),
            ])
    export = StateTransition()
    result = StateView('esale.export.stock.csv.result',
        'esale_stock.esale_export_stock_csv_result', [
            Button('Close', 'end', 'tryton-close'),
            ])

    def transition_export(self):
        pool = Pool()
        Date = pool.get('ir.date')
        Product = pool.get('product.product')

        shop = self.start.shop
        from_date = self.start.from_date

        output = Product.esale_export_stock_csv(shop, from_date)

        self.result.csv_file = fields.Binary.cast(output.getvalue())
        self.result.file_name = '%s-stock-%s.csv' % (
            slugify(shop.name.replace('.', '-')),
            Date.today())
        return 'result'

    def default_result(self, fields):
        return {
            'csv_file': self.result.csv_file,
            'file_name': self.result.file_name,
            }
