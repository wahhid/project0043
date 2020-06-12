from openerp.osv import fields, osv

class account_move(osv.osv):
    _inherit = "account.move"

    _columns = {
        'cust_deposit_id': fields.many2one('cust.deposit', 'Deposit #'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice #', readonly=True)
    }


