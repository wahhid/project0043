from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round
import logging


_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_credit = fields.Monetary('Total Receivable', related="partner_id.credit", readonly=True)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_sale_order_line_multiline_description_sale(self, product):
        _logger.debug('get_sale_order_line_multiline_description_sale')
        ctx = self._context
        if 'sale_order_line_display' in ctx:
            return product.name    
        return super(SaleOrderLine, self).get_sale_order_line_multiline_description_sale(product)


    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product = self.product_id.with_context(
                warehouse=self.order_id.warehouse_id.id,
                lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
            )
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            if float_compare(product.virtual_available, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:
                    message =  _('You plan to sell %s %s of %s but you only have %s %s available in %s warehouse.') % \
                            (self.product_uom_qty, self.product_uom.name, self.product_id.name, product.virtual_available, product.uom_id.name, self.order_id.warehouse_id.name)
                    # We check if some products are available in other warehouses.
                    if float_compare(product.virtual_available, self.product_id.virtual_available, precision_digits=precision) == -1:
                        message += _('\nThere are %s %s available across all warehouses.\n\n') % \
                                (self.product_id.virtual_available, product.uom_id.name)
                        for warehouse in self.env['stock.warehouse'].search([]):
                            quantity = self.product_id.with_context(warehouse=warehouse.id).virtual_available
                            if quantity > 0:
                                message += "%s: %s %s\n" % (warehouse.name, quantity, self.product_id.uom_id.name)
                    warning_mess = {
                        'title': _('Not enough inventory!'),
                        'message' : message
                    }
                    return {'warning': warning_mess}
            else:
                #Check Product Available because sum of several lot
                _logger.info("Check Lot")
                stock_quant_ids = self.env['stock.quant'].search([('product_id','=', self.product_id.id),('quantity','>',0)], order="quantity desc")
                is_multiple_lot = False
                for stock_quant_id in stock_quant_ids:
                    _logger.info(stock_quant_id.quantity)
                    _logger.info(self.product_uom_qty) 
                    if stock_quant_id.quantity < self.product_uom_qty:
                        is_multiple_lot = True
                        break
                
                if is_multiple_lot:
                    warning_mess = {
                        'title': _('Stock Lot Information'),
                        'message' : 'Product Quantity created by sum of several lot!'
                    }
                    return {'warning': warning_mess}
                
        return {}