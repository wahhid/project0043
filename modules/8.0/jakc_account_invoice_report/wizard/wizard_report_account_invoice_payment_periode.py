import time
from openerp.osv import osv, fields


class wizard_account_invoice_payment_periode(osv.osv_memory):
    _name = 'wizard.account.invoice.payment.periode'
    _description = 'Account Invoice Payment Periode'

    _columns = {
        'date_start': fields.date('Date Start', required=True),
        'date_end': fields.date('Date End', required=True),
        'type': fields.selection([('receipt','Sale'),('payment','Purchase')], 'Type'),
    }
    _defaults = {
        'date_start': fields.date.context_today,
        'date_end': fields.date.context_today,
        'type': 'receipt',
    }

    def print_report(self, cr, uid, ids, context=None):
        """
         To get the date and print the report
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return : retrun report
        """
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['date_start', 'date_end', 'type'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return self.pool['report'].get_action(cr, uid, [], 'jakc_account_invoice_report.report_accountinvoicepaymentperiode', data=datas, context=context)

