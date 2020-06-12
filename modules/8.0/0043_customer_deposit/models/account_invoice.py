from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


    @api.multi

    def register_payment_using_deposit(self):

        name = _('Register Payment using Deposit')

        view_mode = 'tree,form'

        ref = self.env.ref("account.view_account_payment_invoice_form")

        return {

            'name': name,

            'view_type': 'form',

            'view_mode': view_mode,

            'res_model': 'account.payment',

            "view_id": ref.id,

            'type': 'ir.actions.act_window',

            'target': 'new',

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



    
    