from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, Warning
from datetime import time

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.one
    def get_sale_order_note(self):
        self.sale_order_note = self.sale_id.note

    iface_return = fields.Boolean('Return', readonly=False, default=False)
    delivery_date  = fields.Date('Delivery Date', default=lambda self: fields.datetime.today())
    sale_order_note = fields.Text('Sale Order Note', compute="get_sale_order_note")