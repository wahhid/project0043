# Copyright 2011 Domsense s.r.l. <http://www.domsense.com>
# Copyright 2013 Lorenzo Battistini <lorenzo.battistini@agilebg.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models
from collections import defaultdict


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"


    def _compute_prod_lots(self):
        for line in self:
            line.prod_lot_ids = line.mapped(
                'move_line_ids.move_line_ids.lot_id'
            )

    def _compute_lot_string(self):
        name = False
        for line in self:
            for lot_id in line.prod_lot_ids:
                #_logger.debug(lot_id)
                name = lot_id[0][0]
            if name:
                line.lot_string = name

    def lots_grouped_by_quantity(self):
        lot_dict = defaultdict(float)
        for sml in self.mapped('move_line_ids.move_line_ids'):
            lot_dict[sml.lot_id.name] += sml.qty_done
        return lot_dict


    lot_string = fields.Many2one('stock.production.lot', 'Lot', compute="_compute_lot_string")


    prod_lot_ids = fields.Many2many(
        comodel_name='stock.production.lot',
        compute='_compute_prod_lots',
        string="Production Lots",
    )

