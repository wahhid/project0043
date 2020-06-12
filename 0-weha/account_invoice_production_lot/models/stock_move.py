from odoo import fields, models
from collections import defaultdict


class StockMove(models.Model):
    _inherit = "stock.move"


    def _compute_prod_lots(self):
        for line in self:
            line.prod_lot_ids = line.mapped(
                'move_ids_without_package.move_line_ids.lot_id'
            )
    
    def _compute_lot_string(self):
        name = False
        for line in self:
            for lot_id in line.prod_lot_ids:
                #_logger.debug(lot_id)
                name = lot_id[0][0]
            if name:
                line.lot_string = name

    prod_lot_ids = fields.Many2many(
        comodel_name='stock.production.lot',
        compute='_compute_prod_lots',
        string="Production Lots",
    )

    lot_string = fields.Many2one('stock.production.lot', 'Lot', compute="_compute_lot_string")