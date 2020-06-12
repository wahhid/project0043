from odoo import models,api,fields,_ 

import logging
_logger = logging.getLogger(__name__)



class StockMove(models.Model):
    _inherit = 'stock.move'

    def _update_reserved_quantity(self, need, available_quantity,
                                  location_id, lot_id=None,
                                  package_id=None, owner_id=None,
                                  strict=True):
        if self._context.get('sol_lot_id'):
            lot_id = self.sale_line_id.lot_id
        return super(StockMove, self)._update_reserved_quantity(
            need, available_quantity, location_id, lot_id=lot_id,
            package_id=package_id, owner_id=owner_id, strict=strict)

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super(StockMove, self)._prepare_move_line_vals(
            quantity=quantity, reserved_quant=reserved_quant)
        lot = self.sale_line_id.lot_id
        if reserved_quant and lot:
            vals['lot_id'] = lot.id
        return vals


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if self._context.get('show_lot_qty'):
                record_name = record.name + ' - ' + str(record.product_qty)
                result.append((record.id, record_name))
            else:
                result.append((record.id, record.name))
        return result