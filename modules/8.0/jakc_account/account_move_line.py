import time
from datetime import datetime

from openerp import workflow
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools
from openerp.report import report_sxw
import openerp


class account_move_line(osv.osv):
    _inherit = 'account.move.line'


    _columns = {
        'deposit_amount': fields.float()
    }
