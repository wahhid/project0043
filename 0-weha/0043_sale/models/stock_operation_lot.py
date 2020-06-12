from odoo import models, fields, api 
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.multi
    def name_get(self):
        ctx = self._context
        if 'show_lot_qty' in ctx:
            if ctx.get('show_lot_qty') == 1:
                res = []
                for rec in self:
                    res.append((rec.id, '%s (%s %s)' % (rec.name, rec.product_qty, rec.product_id.uom_id.name)))
                return res
        return super(StockProductionLot,self).name_get()

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        ctx = self._context
        if 'order_by_qty' in ctx:
            if ctx.get('order_by_qty') == 1:
                order = "product_qty desc"
        res = super(StockProductionLot, self).search(args, offset=offset, limit=limit, order=order, count=count)
        return res


