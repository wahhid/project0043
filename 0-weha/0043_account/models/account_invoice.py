from odoo import models, fields, api,  _ 
from odoo.exceptions import UserError, ValidationError
import logging
from num2words import num2words

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    def get_terbilang(self):
        self.terbilang = num2words(self.amount_total, lang='id').title()

    printed_number = fields.Integer('Printed #', default=0)
    terbilang = fields.Char("Terbilang", size=250 , compute="get_terbilang", readonly=True)

