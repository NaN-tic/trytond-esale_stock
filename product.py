# This file is part esale_stock module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.transaction import Transaction
from trytond.pyson import Eval

__all__ = ['Template', 'EsaleExportStockStart', 'EsaleExportStockResult',
    'EsaleExportStock']
__metaclass__ = PoolMeta


class Template:
    "Product Template"
    __name__ = 'product.template'
    esale_manage_stock = fields.Boolean('Manage Stock',
            help='Manage stock in e-commerce')

    @staticmethod
    def default_esale_manage_stock():
        return True


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
        print "fi"
        return 'result'

    def default_result(self, fields):
        info_ = self.result.info
        return {
            'info': info_,
            }
