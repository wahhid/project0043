from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


    @api.multi
    def register_payment_using_deposit(self):
        if self.residual > self.cust_deposit_id.rest_amount:
            raise ValidationError('Insufficient deposit funds')

        Params = self.env['ir.config_parameter'].sudo()
        customer_deposit_journal_id = Params.get_param('0043_customer_deposit.customer_deposit_journal_id') or False

        name = _('Deposit Payment')
        view_mode = 'form'
        ref = self.env.ref("account.view_account_payment_invoice_form")
        return {
            'name': name,
            'view_type': 'form',
            'view_mode': view_mode,
            'res_model': 'account.payment',
            "view_id": ref.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_journal_id': int(customer_deposit_journal_id),
                'default_is_deposit': self.is_deposit,
                'default_customer_deposit_id': self.cust_deposit_id.id,
            },
        }

    is_deposit = fields.Boolean(
        string='Is Deposit',
        default = False,
    )
    
    cust_deposit_id = fields.Many2one(
        string='Deposit #',
        comodel_name='customer.deposit',
    )
    
    sale_order_id = fields.Many2one(
        string='Sale Order #',
        comodel_name='sale.order',
    )



    
    