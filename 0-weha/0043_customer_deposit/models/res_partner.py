from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'


    def _compute_deposit_amount(self):
        result = {}
         
        Params = self.env['ir.config_parameter'].sudo()
        customer_deposit_account_id = Params.get_param('0043_customer_deposit.customer_deposit_account_id') or False
  
        if not customer_deposit_account_id:
            raise UserError(_('Error!'), _('Please define default deposit account for the company.'))

        sql = """SELECT sum(a.credit - a.debit) as deposit
                FROM account_move_line a
                INNER JOIN account_move b ON a.move_id = b.id
                WHERE a.partner_id=%s AND a.account_id=%s AND b.state=%s"""

        self.env.cr.execute(sql, (self.id, int(customer_deposit_account_id), 'posted',))
        self.deposit_amount = self.env.cr.fetchone()[0]


    def _compute_overpay_amount(self):
        result = {}
         
        Params = self.env['ir.config_parameter'].sudo()
        customer_overpay_account_id = Params.get_param('0043_customer_deposit.customer_overpay_account_id') or False
  
        if not customer_overpay_account_id:
            raise UserError(_('Error!'), _('Please define default overpay account for the company.'))

        sql = """SELECT sum(a.credit - a.debit) as overpay
                FROM account_move_line a
                INNER JOIN account_move b ON a.move_id = b.id
                WHERE a.partner_id=%s AND a.account_id=%s AND b.state=%s"""

        self.env.cr.execute(sql, (self.id, int(customer_overpay_account_id), 'posted',))
        self.overpay_amount = self.env.cr.fetchone()[0]


    deposit_amount = fields.Float('Deposit Balance', compute="_compute_deposit_amount", readonly=True)
    overpay_amount = fields.Float('Overpay Balance', compute="_compute_overpay_amount", readonly=True)