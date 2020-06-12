from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    cust_deposit_id = fields.Many2one('customer.deposit', 'Deposit #')
    invoice_id = fields.Many2one('account.invoice', 'Invoice #', readonly=True)




