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

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def _get_default_sale_person(self, cr, uid, context=None):
        sale_person_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.default_sale_person.id
        _logger.info(sale_person_id)
        if sale_person_id:
            return sale_person_id
        else:
            return False

    _defaults = {
        'user_id': _get_default_sale_person,
    }

    