from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError
import logging


_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    wa1 = fields.Char("WA 1", size=100)
    wa2 = fields.Char("WA 2", size=100)
    no_rek = fields.Char("No Rekening", size=100)
    other_info_row1 = fields.Char("Row 1", size=100)
    other_info_row2 = fields.Char("Row 2", size=100)
    other_info_row3 = fields.Char("Row 3", size=100)
    other_info_row4 = fields.Char("Row 4", size=100)
    other_info_row5 = fields.Char("Row 5", size=100)
    
