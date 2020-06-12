from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round
from openerp.exceptions import except_orm

class product_template(osv.osv):
    _name = 'product.template'
    _inherit = 'product.template'

    def action_open_quants_tree2(self, cr, uid, ids, context=None):
        products = self._get_products(cr, uid, ids, context=context)
        result = self._get_act_window_dict(cr, uid, 'jakc_stock.action_stock_quant_tree2', context=context)
        result['domain'] = "[('product_id','in',[" + ','.join(map(str, products)) + "])]"
        result['context'] = "{'search_default_internal_loc': 1,'search_default_lot_id': 1}"
        return result


