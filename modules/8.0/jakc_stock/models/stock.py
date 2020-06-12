from openerp import  models, fields, api, _
from openerp.exceptions import ValidationError, Warning
from datetime import datetime

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_date  = fields.Date('Delivery Date', default=datetime.today())

class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.one
    def calculate_total_qty_diff(self):
        total_qty_diff = 0
        for line in self.line_ids:
            total_qty_diff = total_qty_diff + line.qty_diff
        self.total_qty_diff = total_qty_diff

    @api.one
    def calculate_total_qty_product(self):
        total_qty_diff = 0
        for line in self.line_ids:
            total_qty_diff = total_qty_diff + line.qty_diff
        self.total_qty_diff = total_qty_diff

    @api.one
    def calculate_total_qty_real(self):
        total_qty_diff = 0
        for line in self.line_ids:
            total_qty_diff = total_qty_diff + line.qty_diff
        self.total_qty_diff = total_qty_diff

    total_qty_diff = fields.Float('Total Diff', compute='calculate_total_qty_diff',readonly=True)
    #total_qty_product = fields.Float('Total Stok Komputer', compute='', readonly=True)
    #total_qty_real = fields.Float('Total Hsl Opname', compute='', readonly=True)


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    @api.one
    def calculate_qty_diff(self):
        self.qty_diff = self.product_qty - self.theoretical_qty

    qty_diff = fields.Float('Diff', compute='calculate_qty_diff', readonly=True)