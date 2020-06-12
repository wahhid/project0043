from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_deposit = fields.Boolean(
        string='Is Deposit',
        default = False,
    )
    
