import time
from datetime import datetime

from openerp import workflow
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools
from openerp.report import report_sxw
import openerp
import logging



_logger = logging.getLogger(__name__)

class account_voucher(osv.osv):
    _inherit = 'account.voucher'

    def _get_company(self, cr, uid, context=None):
        return self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id

    def _get_deposits(self, cr, uid, partner_id, context=None):
        cust_deposit_partner_obj = self.pool.get('cust.deposit.partner')
        args = [('partner_id','=', partner_id)]
        ids = cust_deposit_partner_obj.search(cr, uid, args, context=context)
        cust_deposit_partner_ids = cust_deposit_partner_obj.browse(cr, uid, ids, [])
        deposits = ()
        for cust_deposit_partner_id in cust_deposit_partner_ids:
            if cust_deposit_partner_id.id not in deposits:
                deposits = deposits + (cust_deposit_partner_id.cust_deposit_id.id,)
        _logger.info("Deposit")
        _logger.info(deposits)
        return deposits

    #def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=None):

    #    res = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=context)

    #    invoice_pool = self.pool.get('account.invoice')
    #    journal_pool = self.pool.get('account.journal')
    #    journal = journal_pool.browse(cr, uid, journal_id, context=context)
    #    company = self._get_company(cr, uid, context=context)

    #    if journal:
    #        company = self.pool.get('res.company').browse(cr, uid, company.id, context=context)
    #        if company.deposit_journal_id.id == journal.id:
    #            # Get Customer Deposit Amount
    #            if context.get('invoice_id', False):
    #                invoice = invoice_pool.browse(cr, uid, context['invoice_id'], context=context)
    #                if invoice.type == 'out_invoice':
    #                    sale_id = invoice.sale_ids[0]
    #                    deposit_id = sale_id.cust_deposit_id
    #                    res['value']['cust_deposit_id'] = deposit_id.id
    #                    res['value']['deposit'] = deposit_id.rest_amount
    #                if invoice.type == 'out_refund':
    #                    res['value']['iface_deposit'] = True
    #            else:
    #                res['value']['deposit'] = 0.0
    #        else:
    #            res['value']['deposit'] = 0.0

    #        if company.overpay_journal_id.id == journal.id:
    #            # Get Customer Overpay Amount
    #            if context.get('invoice_id', False):
    #                invoice = invoice_pool.browse(cr, uid, context['invoice_id'], context=context)
    #                if invoice.type == 'out_invoice':
    #                    sale_id = invoice.sale_ids[0]
    #                    partner_id  = sale_id.partner_id
    #                    res['value']['overpay'] = partner_id.overpay
    #            else:
    #                res['value']['deposit'] = 0.0
    #        else:
    #            res['value']['deposit'] = 0.0
    #
    #        deposits = self._get_deposits(cr, uid, partner_id, context=context)
    #        #res['domain']={'cust_deposit_id':[('id', 'in', deposits)]}

    #    return res

    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):

        vals = super(account_voucher, self).onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=context)

        invoice_pool = self.pool.get('account.invoice')
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)

        if journal:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            if company.deposit_journal_id.id == journal.id:
                #Get Customer Deposit Amount
                if context.get('invoice_id', False):
                    invoice = invoice_pool.browse(cr, uid, context['invoice_id'], context=context)
                    if invoice.type == 'out_invoice':
                        sale_id = invoice.sale_ids[0]                       
                        if sale_id.iface_deposit:
                            deposit_id = sale_id.cust_deposit_id
                            vals['value']['cust_deposit_id'] = deposit_id.id
                            vals['value']['deposit'] = deposit_id.rest_amount
                        else:
                            vals['value']['iface_deposit'] = True
                    if invoice.type == 'out_refund':
                        _logger.info('Out Refund')
                        vals['value']['iface_deposit'] = True
                else:
                    vals['value']['deposit'] = 0.0
            else:
                vals['value']['iface_deposit'] = False
                vals['value']['deposit'] = 0.0

            if company.overpay_journal_id.id == journal.id:
                # Get Customer Overpay Amount
                if context.get('invoice_id', False):
                    invoice = invoice_pool.browse(cr, uid, context['invoice_id'], context=context)
                    if invoice.type == 'out_invoice':
                        sale_id = invoice.sale_ids[0]
                        partner_id  = sale_id.partner_id
                        vals['value']['overpay'] = partner_id.overpay
                        if amount > partner_id.overpay:
                            vals['value']['amount']  = partner_id.overpay
                else:
                    if vals['value']['deposit'] > 0.0:
                        vals['value']['deposit'] = 0.0
                        _logger.info('overpay 1')
                        _logger.info(vals['value']['deposit'])
            #else:
            #    if vals['value']['deposit'] > 0.0:
            #        vals['value']['deposit'] = 0.0
            #        _logger.info('overpay 2')
            deposits = self._get_deposits(cr, uid, partner_id, context=context)
            vals['domain']={'cust_deposit_id':[('id', 'in', deposits)]}
        return vals


    def onchange_deposit(self, cr, uid, ids, cust_deposit_id, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):

        vals = super(account_voucher, self).onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=context)

        invoice_pool = self.pool.get('account.invoice')
        journal_pool = self.pool.get('account.journal')
        cust_deposit_pool = self.pool.get('cust.deposit')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)

        if journal:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            if company.deposit_journal_id.id == journal.id:
                #Get Customer Deposit Amount
                if context.get('invoice_id', False):
                    invoice = invoice_pool.browse(cr, uid, context['invoice_id'], context=context)
                    if invoice.type == 'out_invoice':
                        sale_id = invoice.sale_ids[0]                       
                        if sale_id.iface_deposit:
                            deposit_id = sale_id.cust_deposit_id
                            vals['value']['cust_deposit_id'] = deposit_id.id
                            vals['value']['deposit'] = deposit_id.rest_amount
                        else:
                            deposit_id = cust_deposit_pool.browse(cr, uid, cust_deposit_id, context=context)
                            vals['value']['iface_deposit'] = True
                            vals['value']['deposit'] = deposit_id.rest_amount
                    if invoice.type == 'out_refund':
                        _logger.info('Out Refund')
                        vals['value']['iface_deposit'] = True
                else:
                    vals['value']['deposit'] = 0.0
            else:
                vals['value']['iface_deposit'] = False
                vals['value']['deposit'] = 0.0

            if company.overpay_journal_id.id == journal.id:
                # Get Customer Overpay Amount
                if context.get('invoice_id', False):
                    invoice = invoice_pool.browse(cr, uid, context['invoice_id'], context=context)
                    if invoice.type == 'out_invoice':
                        sale_id = invoice.sale_ids[0]
                        partner_id  = sale_id.partner_id
                        vals['value']['overpay'] = partner_id.overpay
                        if amount > partner_id.overpay:
                            vals['value']['amount']  = partner_id.overpay
                else:
                    if vals['value']['deposit'] > 0.0:
                        vals['value']['deposit'] = 0.0
                        _logger.info('overpay 1')
                        _logger.info(vals['value']['deposit'])
            #else:
            #    if vals['value']['deposit'] > 0.0:
            #        vals['value']['deposit'] = 0.0
            #        _logger.info('overpay 2')
            deposits = self._get_deposits(cr, uid, partner_id, context=context)
            vals['domain']={'cust_deposit_id':[('id', 'in', deposits)]}
        return vals

    def writeoff_move_line_get(self, cr, uid, voucher_id, line_total, move_id, name, company_currency,
                                   current_currency, context=None):
        '''
        Set a dict to be use to create the writeoff move line.

        :param voucher_id: Id of voucher what we are creating account_move.
        :param line_total: Amount remaining to be allocated on lines.
        :param move_id: Id of account move where this line will be added.
        :param name: Description of account move line.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: mapping between fieldname and value of account move line to create
        :rtype: dict
        '''

        _logger.warning('writeoff_move_line_get')
        currency_obj = self.pool.get('res.currency')
        move_line = {}

        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context)
        current_currency_obj = voucher.currency_id or voucher.journal_id.company_id.currency_id

        if not currency_obj.is_zero(cr, uid, current_currency_obj, line_total):
            diff = line_total
            account_id = False
            write_off_name = ''
            if voucher.payment_option == 'with_writeoff':
                _logger.warning('With Writeoff')
                account_id = voucher.writeoff_acc_id.id
                write_off_name = voucher.comment
            elif voucher.payment_option == 'deposit':
                _logger.warning('Deposit')
                company = self._get_company(cr, uid, context=context)
                account_id = company.deposit_account_id.id
                write_off_name = 'Customer Deposit'
            elif voucher.payment_option == 'overpay':
                _logger.warning('Overpay')
                company = self._get_company(cr, uid, context=context)
                account_id = company.overpay_account_id.id
                write_off_name = 'Overpay Deposit'
            elif voucher.partner_id:
                if voucher.type in ('sale', 'receipt'):
                    account_id = voucher.partner_id.property_account_receivable.id
                else:
                    account_id = voucher.partner_id.property_account_payable.id
            else:
                # fallback on account of voucher
                account_id = voucher.account_id.id
            sign = voucher.type == 'payment' and -1 or 1
            move_line = {
                'name': write_off_name or name,
                'account_id': account_id,
                'move_id': move_id,
                'partner_id': voucher.partner_id.id,
                'date': voucher.date,
                'credit': diff > 0 and diff or 0.0,
                'debit': diff < 0 and -diff or 0.0,
                'amount_currency': company_currency <> current_currency and (
                    sign * -1 * voucher.writeoff_amount) or 0.0,
                'currency_id': company_currency <> current_currency and current_currency or False,
                'analytic_account_id': voucher.analytic_id and voucher.analytic_id.id or False,
            }

        return move_line

    def button_proforma_voucher(self, cr, uid, ids, context=None):
        cust_deposit_pool = self.pool.get('cust.deposit')
        company = self._get_company(cr, uid, context=context)
        for voucher in self.browse(cr, uid, ids, context=context):
            _logger.info("Amount")
            _logger.info(voucher.amount)
            _logger.info("Overpay")
            _logger.info(voucher.partner_id.overpay)
            if company.deposit_journal_id.id == voucher.journal_id.id:
                if voucher.amount > voucher.cust_deposit_id.rest_amount:
                    raise osv.except_osv(_('Error!'), _('Cannot Process due Deposit not enough'))
            if company.overpay_journal_id.id == voucher.journal_id.id:
                if voucher.amount > voucher.partner_id.overpay:
                    raise osv.except_osv(_('Error!'), _('Cannot Process due Overpay Deposit not enough'))
        return super(account_voucher, self).button_proforma_voucher(cr, uid, ids, context=context)

    def account_move_get(self, cr, uid, voucher_id, context=None):
        _logger.warning('account_move_get')
        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context)
        move = super(account_voucher, self).account_move_get(cr, uid, voucher_id, context=context)
        _logger.warning(voucher.cust_deposit_id.id)
        move.update({'cust_deposit_id': voucher.cust_deposit_id.id})
        print move
        return move

    def action_move_line_create(self, cr, uid, ids, context=None):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        _logger.info("action_move_line_create")
        _logger.info(context)

        if context is None:
            context = {}
        
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        invoice_pool = self.pool.get('account.invoice')
        
        invoice_id = context.get('invoice_id', False)
        _logger.info("Invoice ID")
        _logger.info(invoice_id)
        
        for voucher in self.browse(cr, uid, ids, context=context):
            local_context = dict(context, force_company=voucher.journal_id.company_id.id)
            if voucher.move_id:
                continue
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            # we select the context to use accordingly if it's a multicurrency case or not
            context = self._sel_context(cr, uid, voucher.id, context)
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = context.copy()
            ctx.update({'date': voucher.date})
            # Create the account move record.
            move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
            # WEHA - Update Invoice ID
            if invoice_id:
                move_pool.write(cr, uid, [move_id],  {'invoice_id': invoice_id}, context=context)
            # Get the name of the account_move just created
            name = move_pool.browse(cr, uid, move_id, context=context).name
            # Create the first line of the voucher
            move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, local_context), local_context)
            move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
            line_total = move_line_brw.debit - move_line_brw.credit
            rec_list_ids = []
            if voucher.type == 'sale':
                line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            elif voucher.type == 'purchase':
                line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            # Create one move line per voucher line where amount is not 0.0
            line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)

            # Create the writeoff line if needed
            ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, local_context)
            if ml_writeoff:
                move_line_pool.create(cr, uid, ml_writeoff, local_context)
            # We post the voucher.
            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            if voucher.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context={})
            # We automatically reconcile the account move lines.
            reconcile = False
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
        return True

    _columns = {
        'deposit': fields.float('Deposit Amount', readonly=True),
        'cust_deposit_id': fields.many2one('cust.deposit','Deposit', readonly=False),
        'iface_deposit': fields.boolean('Is Deposit', readonly=True),
        'overpay': fields.float('Overpay Amount', readonly=True),
        #'pricelist_id': fields.related('cust_deposit_id','pricelist_id', type="many2one", relation="product.pricelist", string="Pricelist", readonly=True),
        #'rest_amount': fields.related('cust_deposit_id','rest_amount', type="float", string="Rest Amount"),
        'payment_option': fields.selection([
            ('without_writeoff', 'Keep Open'),
            ('with_writeoff', 'Reconcile Payment Balance'),
            ('deposit', 'Deposit Account'),
            ('overpay', 'Overpay Account'),
        ], 'Payment Difference', required=True, readonly=True, states={'draft': [('readonly', False)]},
            help="This field helps you to choose what you want to do with the eventual difference between the paid amount and the sum of allocated amounts. You can either choose to keep open this difference on the partner's account, or reconcile it with the payment(s)"),
    }

    _defaults = {
        'iface_deposit': lambda *a: False,
    }