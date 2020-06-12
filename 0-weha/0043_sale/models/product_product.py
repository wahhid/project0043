from odoo import models, fields, api 
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def name_get(self):
        ctx = self._context
        if 'sale_order_line_display' in ctx:
            if ctx.get('sale_order_line_display') == 1:
                res = []
                for rec in self:
                    res.append((rec.id, '%s' % (rec.default_code)))
                return res
        return super(ProductProduct,self).name_get()


