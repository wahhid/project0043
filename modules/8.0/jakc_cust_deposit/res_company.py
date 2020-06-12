from openerp.osv import fields, osv


class res_company(osv.osv):
    _inherit = 'res.company'

    _columns =  {
        'deposit_pricelist_id': fields.many2one('product.pricelist', 'Pricelist'),
        'deposit_journal_id' : fields.many2one('account.journal','Deposit Journal'),
        'deposit_account_id' : fields.many2one('account.account','Deposit Account'),
        'overpay_journal_id' : fields.many2one('account.journal','Overpay Journal'),
        'overpay_account_id' : fields.many2one('account.account','Overpay Account'),
    }

