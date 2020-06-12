# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
import pytz
import time
from openerp import tools
from openerp.osv import osv
from openerp.report import report_sxw


class deposit_details(report_sxw.rml_parse):

    def _get_all_users(self):
        user_obj = self.pool.get('res.users')
        return user_obj.search(self.cr, self.uid, [])


    def _get_selected_partners(self, form):
        partner_obj = self.pool.get('res.partner')
        partner_args = [('id','in',form['partner_ids'])]
        partner_ids = partner_obj.search(self.cr, self.uid, partner_args)
        return partner_obj.browse(self.cr, self.uid, partner_ids,[])

    def _get_customer_deposit_balance(self, start_date, partner_id):
        data = []
        result = {}
        balance = 0
        user_obj = self.pool.get('res.users')
        company = user_obj.browse(self.cr, self.uid, self.uid, []).company_id
        deposit_account_id = company.deposit_account_id.id
        account_move_line_obj = self.pool.get('account.move.line')
        account_move_line_args = [('partner_id','=',partner_id),
                                  ('account_id','=',deposit_account_id),
                                  ('date','<', start_date)]        
        account_move_line_ids = account_move_line_obj.search(self.cr, self.uid, account_move_line_args)
        account_move_lines = account_move_line_obj.browse(self.cr, self.uid, account_move_line_ids, [])
        for account_move_line in account_move_lines:
            balance = balance + account_move_line.credit - account_move_line.debit
        return balance

    def _get_account_move_line(self, form, partner_id):
        balance = self._get_customer_deposit_balance(form['start_date'], partner_id)
        data = []
        result = {}
        user_obj = self.pool.get('res.users')
        company = user_obj.browse(self.cr, self.uid, self.uid, []).company_id
        deposit_account_id = company.deposit_account_id.id
        account_move_line_obj = self.pool.get('account.move.line')
        account_move_line_args = [('partner_id','=',partner_id),
                                  ('account_id','=',deposit_account_id),
                                  ('date','>=', form['start_date']),
                                  ('date','<=', form['end_date'])]
        account_move_line_ids = account_move_line_obj.search(self.cr, self.uid, account_move_line_args, order='date asc')
        account_move_lines = account_move_line_obj.browse(self.cr, self.uid, account_move_line_ids, [])
        account_invoice_obj = self.pool.get('account.invoice')
        account_voucher_obj = self.pool.get('account.voucher')
        for account_move_line in account_move_lines:
            
            account_invoice_ids = account_invoice_obj.search(self.cr, self.uid, [('move_id','=', account_move_line.move_id.id)])
            account_voucher_ids = account_voucher_obj.search(self.cr, self.uid, [('move_id','=', account_move_line.move_id.id)])
            
            number = 'No Trans #'
            if len(account_voucher_ids) > 0:
                account_voucher_id = account_voucher_obj.browse(self.cr, self.uid, account_voucher_ids[0])
                number = account_voucher_id.number 
            balance = balance + account_move_line.credit - account_move_line.debit
            result = {
                'date': account_move_line.date,
                'name': account_move_line.move_id.name,
                'number': number,
                'debit': account_move_line.debit,
                'credit': account_move_line.credit,
                'balance': balance
            }
            data.append(result)
        if data:
            return data
        else:
            return {}

    def __init__(self, cr, uid, name, context=None):
        super(deposit_details, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'selected_partners': self._get_selected_partners,
            'account_move_lines': self._get_account_move_line,
        })
        self.context = context


class report_jakc_cust_deposit(osv.AbstractModel):
    _name = 'report.jakc_cust_deposit.report_custdeposit'
    _inherit = 'report.abstract_report'
    _template = 'jakc_cust_deposit.report_custdeposit'
    _wrapped_report_class = deposit_details
