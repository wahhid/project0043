import time
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare, float_is_zero
from openerp.osv import fields, osv
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import pytz
from openerp import SUPERUSER_ID

import logging

_logger = logging.getLogger(__name__)

class sale_order(osv.osv):
    _inherit = 'sale.order'

    def get_access_for_amount_total(self, cr, uid, ids, fields, args, context=None):
        return self.pool.get('res.users').has_group(cr, uid, 'base.group_sale_store')

    _columns = {
        'iface_able_to_read_amount_total':fields.function(get_access_for_amount_total, type='boolean', string='Is user able to see amount product?'),
        'user_id': fields.many2one('res.users', 'Salesperson', required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, select=True, track_visibility='onchange'),
    }


    #def action_wait(self, cr, uid, ids, context=None):
    #    sale_order_obj = self.pool.get('sale.order')
    #    sale_order = self.browse(cr, uid, ids[0], context=context)
    #    partner_id = sale_order.partner_id
    #    args = [('state','in',['progress','manual'])]
    #    sale_order_ids =  sale_order_obj.search(cr, uid, args, context=context)
    #    if sale_order_ids:
    #        raise osv.except_osv(_('Error!'), _('You cannot confirm a sales order because customer still have outstanding sale order or invoice.'))
    #    else:
    #        super(sale_order,self).action_wait(cr, uid, ids, context=context)
    #    return True

sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    def product_id_change_with_wh(self, cr, uid, ids, pricelist, product, qty=0,
                                  uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                                  lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False,
                                  flag=False, warehouse_id=False, context=None):
        context = context or {}
        product_uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        warning = {}
        # UoM False due to hack which makes sure uom changes price, ... in product_id_change
        res = self.product_id_change(cr, uid, ids, pricelist, product, qty=qty,
                                     uom=False, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
                                     lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging,
                                     fiscal_position=fiscal_position, flag=flag, context=context)

        if not product:
            res['value'].update({'product_packaging': False})
            return res

        # set product uom in context to get virtual stock in current uom
        if 'product_uom' in res.get('value', {}):
            # use the uom changed by super call
            context = dict(context, uom=res['value']['product_uom'])
        elif uom:
            # fallback on selected
            context = dict(context, uom=uom)

        # update of result obtained in super function
        product_obj = product_obj.browse(cr, uid, product, context=context)
        res['value'].update(
            {'product_tmpl_id': product_obj.product_tmpl_id.id, 'delay': (product_obj.sale_delay or 0.0)})

        # Calling product_packaging_change function after updating UoM
        res_packing = self.product_packaging_change(cr, uid, ids, pricelist, product, qty, uom, partner_id, packaging,
                                                    context=context)
        res['value'].update(res_packing.get('value', {}))
        warning_msgs = res_packing.get('warning') and res_packing['warning']['message'] or ''

        if product_obj.type == 'product':
            # determine if the product needs further check for stock availibility
            is_available = self._check_routing(cr, uid, ids, product_obj, warehouse_id, context=context)

            # check if product is available, and if not: raise a warning, but do this only for products that aren't processed in MTO
            if not is_available:
                uom_record = False
                if uom:
                    uom_record = product_uom_obj.browse(cr, uid, uom, context=context)
                    if product_obj.uom_id.category_id.id != uom_record.category_id.id:
                        uom_record = False
                if not uom_record:
                    uom_record = product_obj.uom_id
                compare_qty = float_compare(product_obj.virtual_available, qty, precision_rounding=uom_record.rounding)
                if compare_qty == -1:
                    warn_msg = _('(%.2f)') % (qty)
                    warning_msgs += _("Not enough stock ! : ") + warn_msg + "\n\n"

        # update of warning messages
        if warning_msgs:
            warning = {
                'title': _('Configuration Error!'),
                'message': warning_msgs
            }
        res.update({'warning': warning})
        return res

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False,
            flag=False, context=None):

        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
                                                                uom, qty_uos, uos, name, partner_id,lang, update_tax,
                                                                date_order, packaging, fiscal_position, flag)

        product_obj = self.pool.get('product.product')
        product_template_obj = self.pool.get('product.template')
        context_partner = context.copy()
        context_partner.update({'lang': lang, 'partner_id': partner_id})
        product_id = self.pool.get('product.product').browse(cr, uid, product, context=context_partner)
        product_template_id =  product_template_obj.browse(cr, uid, product_id.product_tmpl_id.id, context=context)
        if product_id:
            _logger.info(product_id.name)
            result['value']['name'] = product_obj.name_get(cr, uid, [product_id.id], context=context_partner)[0][1]
            if product_template_id:
                if product_id.description_sale:
                    _logger.info(product_id.description_sale)
                    result['value']['name'] = result['value']['name'] + ' ' + product_id.description_sale + ' ' + (product_template_id.motif or '') + ' ' + (product_template_id.warna  or  '') + ' ' + (product_template_id.page or '')
                else:
                    _logger.info("No Description Sale")
                    result['value']['name'] = result['value']['name'] + ' ' + (product_template_id.motif or '') + ' ' + (product_template_id.warna or '') + ' ' + (product_template_id.page or '')
            else:
                result['value']['name'] =  result['value']['name'] + ' ' + product_id.description_sale

        return result

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        res = super(sale_order_line, self)._prepare_order_line_invoice_line(cr, uid, line, account_id=account_id,
                                                                       context=context)
        res['lot_id'] = line.lot_id.id
        _logger.info("Execute Prepare Order Line Invoice Line")
        return res

    _columns = {
        'merk_id': fields.related('product_id', 'merk_id', type="many2one", relation="product.merk", string="Merk", readonly=True),
        'product_uom_qty': fields.float('Qty', digits_compute= dp.get_precision('Product UoS'), required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'product_uom': fields.many2one('product.uom', 'Uom ', required=True, readonly=True, states={'draft': [('readonly', False)]}),
    }

sale_order_line()


from openerp import  models, fields, api, _
from openerp.exceptions import ValidationError, Warning
from datetime import datetime



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_credit = fields.Float("Piutang Belum Terbayar", related='partner_id.credit', store=True)