from datetime import datetime
import pytz
import time
from openerp import tools
from openerp.osv import osv
from openerp.report import report_sxw
import logging

_logger = logging.getLogger(__name__)


class picking_courier(report_sxw.rml_parse):

        
    def __init__(self, cr, uid, name, context):
        super(picking_courier, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'datetime': datetime,
        })


class report_picking_courier(osv.AbstractModel):
    _name = 'report.jakc_stock_report.report_pickingcourier'
    _inherit = 'report.abstract_report'
    _template = 'jakc_stock_report.report_pickingcourier'
    _wrapped_report_class = picking_courier