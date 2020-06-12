from datetime import datetime
import pytz
import time
from openerp import tools
from openerp.osv import osv
from openerp.report import report_sxw
import logging

_logger = logging.getLogger(__name__)


class account_invoice_payment_periode(report_sxw.rml_parse):

    def _get_account_voucher_periode(self, form):
        account_voucher_obj = self.pool.get('account.voucher')
        user_obj = self.pool.get('res.users')
        data = []
        result = {}
        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        date_start = form['date_start']
        date_end = form['date_end']

        account_voucher_ids = account_voucher_obj.search(self.cr, self.uid, [
            ('date', '>=', date_start),
            ('date', '<', date_end),
            ('state', 'in', ['posted']),
            ('type','=', form['type']),
            ('company_id', '=', company_id)
        ])

        for account_voucher_id in account_voucher_obj.browse(self.cr, self.uid, account_voucher_ids, context=self.localcontext):
            result = {
                'number': account_voucher_id.number,
                'date': account_voucher_id.date,
                'partner_id': account_voucher_id.partner_id.name,
                'journal_id': account_voucher_id.journal_id.name,
                'amount': account_voucher_id.amount,
            }
            data.append(result)
        if data:
            return data
        else:
            return {}

    def __init__(self, cr, uid, name, context):
        super(account_invoice_payment_periode, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'datetime': datetime,
            'get_vouchers':self._get_account_voucher_periode,
        })


class report_account_invoice_payment_periode(osv.AbstractModel):
    _name = 'report.jakc_account_invoice_report.report_accountinvoicepaymentperiode'
    _inherit = 'report.abstract_report'
    _template = 'jakc_account_invoice_report.report_accountinvoicepaymentperiode'
    _wrapped_report_class = account_invoice_payment_periode