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

class res_company(osv.osv):
    _inherit = 'res.company'

    _columns = {
        'default_sale_person': fields.many2one('res.users', 'Salesperson'),
    }

   