from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging


_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.onchange('journal_id')
    def _onchange_journal(self):
        res = super(AccountPayment, self)._onchange_journal()
        if self.journal_id.is_deposit:
            values = {
                'is_deposit': True,
            }
            self.update(values)
        else:
            values = {
                'is_deposit': False,
            }
            self.update(values)
        return res

    is_deposit = fields.Boolean(
        string='Is Deposit',
        default = False,
    )

    
    customer_deposit_id = fields.Many2one(
        string='Deposit #',
        comodel_name='customer.deposit',
    )
    