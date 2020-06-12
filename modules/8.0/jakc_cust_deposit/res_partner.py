import time
from datetime import datetime

from openerp import workflow
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools
from openerp.report import report_sxw
import openerp


class res_partner(osv.osv):
    _inherit = 'res.partner'

    def _get_company(self, cr, uid, context=None):
        return self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id

    def _compute_deposit_amount(self, cr, uid, ids, fields, arg, context=None):
        result = {}
        partner_id = ids[0]
        company_id = self._get_company(cr, uid, context=context)

        if not company_id.deposit_journal_id:
            raise osv.except_osv(_('Error!'), _('Please define default deposit journal for the company.') )

        sql = """SELECT sum(a.credit - a.debit) as deposit
                FROM account_move_line a
                INNER JOIN account_move b ON a.move_id = b.id
                WHERE a.partner_id=%s AND a.account_id=%s AND b.state=%s"""

        cr.execute(sql, (partner_id, company_id.deposit_account_id.id, 'posted',))
        result[partner_id] = cr.fetchone()[0]
        return result

    def _compute_overpay_amount(self, cr, uid, ids, fields, arg, context=None):
        result = {}

        for partner_id in self.browse(cr, uid, ids,context=context):
            company_id = self._get_company(cr, uid, context=context)

            if not company_id.overpay_journal_id:
                raise osv.except_osv(_('Error!'), _('Please define default overpay journal for the company.'))

            sql = """SELECT sum(a.credit - a.debit) as overpay
                            FROM account_move_line a
                            INNER JOIN account_move b ON a.move_id = b.id
                            WHERE a.partner_id=%s AND a.account_id=%s AND b.state=%s"""

            cr.execute(sql, (partner_id.id, company_id.overpay_account_id.id, 'posted',))
            result[partner_id.id] = cr.fetchone()[0]

        return result

    _columns = {
        'deposit': fields.function(_compute_deposit_amount, type='float', string='Deposit Amount', groups='account.group_account_invoice'),
        'overpay': fields.function(_compute_overpay_amount, type='float', string='Overpay Amount',groups='account.group_account_invoice'),
        'cust_deposit_ids': fields.one2many('cust.deposit','partner_id','Deposit', readonly=True),
    }