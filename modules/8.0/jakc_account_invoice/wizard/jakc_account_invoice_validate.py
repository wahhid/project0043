import time
from openerp.osv import osv, fields


class account_invoice_validate(osv.osv_memory):
    _name = 'account.invoice.validate'
    _description = 'Account Invoice Validate'

    def account_invoice_validate(self, cr, uid, ids, context=None):
        return self.pool.get('account.invoice').account_invoice_validate(cr, uid, [context.get('invoice_id')], context=context)