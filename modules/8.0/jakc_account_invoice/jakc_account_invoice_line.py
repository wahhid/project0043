from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'

    uos_id = fields.Many2one('product.uom', string='UOM',
                             ondelete='set null', index=True)

    quantity = fields.Float(string='Qty', digits=dp.get_precision('Product Unit of Measure'),
                            required=True, default=1)

