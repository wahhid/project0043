import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp


class ResCompany(models.Model):
    _inherit = 'res.company'

    wa1 = fields.Char('WA 1', size=50)
    wa2 = fields.Char('WA 2', size=50)
    no_rek = fields.Char('No Rekening', size=50)

    other_info_row1 = fields.Char('Row 1', size=100)
    other_info_row2 = fields.Char('Row 2', size=100)
    other_info_row3 = fields.Char('Row 3', size=100)
    other_info_row4 = fields.Char('Row 4', size=100)