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

AVAILABLE_STATES = [
    ('draft','New'),
    ('open','Open'),
    ('confirm','Confirm'),
    ('done','Close'),
    ('post','Posted'),
    ('cancel','Cancelled'),
]

AVAILABLE_DEPOSIT = [
    ('cash','Cash'),
    ('transfer','Transfer'),
    ('cheque','Cheque'),
]

class jakc_cust_deposit(osv.osv):
    _name = "cust.deposit"
    _description = "Customer Deposit"

    def _get_partner(self, cr, uid, partner_id, context=None):
        return self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)

    def _get_company(self, cr, uid, context=None):
        return self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id

    def _generate_priclist(self, cr, uid, context=None):
        print "Generate Pricelist"

    def _generate_public_pricelist(self, cr, uid, version_id, context=None):
        print "Generate Public Pricelist"
        product_pricelist_item_obj = self.pool.get('product.pricelist.item')
        vals = {}
        vals.update({'price_version_id': version_id})
        vals.update({'sequence': 99})
        vals.update({'base': 1})
        res = product_pricelist_item_obj.create(cr, uid, vals, context=context)

    def trans_confirm(self, cr, uid, ids, context=None):
        cust_deposit_obj = self.pool.get('cust.deposit')
        deposit = self.browse(cr, uid, ids, context=context)[0]
        pricelist_id = deposit.pricelist_id
        version_id = pricelist_id.version_id[0]
        self._generate_public_pricelist(cr, uid, version_id.id, context=context)
        cust_deposit_obj.write(cr, uid, ids, {'state':'open'}, context=context)

    def calculate_rest_amount(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        company_id = self._get_company(cr, uid, context=context)
        if not company_id.deposit_journal_id:
            raise osv.except_osv(_('Error!'), _('Please define default deposit journal for the company.'))

        for deposit in self.browse(cr, uid, ids, context=context):
            sql = """SELECT sum(a.credit - a.debit) as rest_amount
                            FROM account_move_line a
                            INNER JOIN account_move b ON a.move_id = b.id
                            WHERE b.cust_deposit_id=%s AND a.account_id=%s"""

            cr.execute(sql, (deposit.id, company_id.deposit_account_id.id))
            result[deposit.id] = cr.fetchone()[0]

        return result

    def _auto_create_pricelist(self, cr, uid, partner_id, context=None):
        pricelist_obj = self.pool.get('product.pricelist')
        pricelist_version_obj = self.pool.get('product.pricelist.version')
        partner = self._get_partner(cr, uid, partner_id, context=context)
        pricelist_vals = {}
        pricelist_vals.update({'name': 'Pricelist - ' + partner.name})
        pricelist_vals.update({'type': 'sale'})
        pricelist_vals.update({'iface_deposit': True})
        pricelist_id = pricelist_obj.create(cr, uid, pricelist_vals, context=context)
        vals = {}
        vals.update({'name': partner.name + ' -  Deposit Version'})
        vals.update({'pricelist_id': pricelist_id})
        pricelist_version_id = pricelist_version_obj.create(cr, uid, vals, context=context)
        return pricelist_id

    _columns = {
        'name': fields.char('Name', size=50),
        'trans_number': fields.char('', size=20, readonly=True),
        'trans_date': fields.date('Transaction Date', required=True),
        'partner_id': fields.many2one('res.partner','Partner  # ', required=True),
        'pricelist_id': fields.many2one('product.pricelist','Pricelist', readonly=True),
        'iface_generated': fields.boolean('Generated', readonly=True),
        'rest_amount': fields.function(calculate_rest_amount, string='Rest Amount', type='float', method=True, readonly=True),
        'payment_ids': fields.one2many('cust.deposit.payment', 'cust_deposit', 'Payments'),
        'product_ids': fields.one2many('cust.deposit.product', 'cust_deposit_id', 'Products'),
        'partner_ids': fields.one2many('cust.deposit.partner', 'cust_deposit_id', 'Partners'),
        'account_move_ids': fields.one2many('account.move', 'cust_deposit_id', 'Moves'),
        'state': fields.selection(AVAILABLE_STATES, 'Status', readonly=True),
    }

    def create(self, cr, uid, vals, context=None):
        trans_number = datetime.now().strftime('%Y%m%d%H%M%S')
        vals.update({'trans_number': trans_number})
        pricelist_id = self._auto_create_pricelist(cr, uid, vals.get('partner_id'), context=context)
        vals.update({'pricelist_id': pricelist_id})
        return super(jakc_cust_deposit, self).create(cr, uid, vals, context=context)


    _defaults = {
        'state': lambda *a: 'draft',
    }

class jakc_cust_deposit_product(osv.osv):
    _name = 'cust.deposit.product'

    def _get_product(self, cr, uid, product_id, context=None):
        product_template_obj = self.pool.get('product.template')
        product_template = product_template_obj.browse(cr, uid, product_id, context=context )
        return product_template

    def _get_product_category(self, cr, uid, product_id, context=None):
        product_category_obj = self.pool.get('product.category')
        product_category = product_category_obj.browse(cr, uid, product_id, context=context)
        return product_category

    def _get_product_merk(self, cr, uid, product_id, context=None):
        product_merk_obj = self.pool.get('product.merk')
        product_merk = product_merk_obj.browse(cr, uid, product_id, context=context)
        return product_merk

    def _add_product_version(self, cr, uid, cust_deposit_product_id, context=None):
        cust_deposit_obj = self.pool.get('cust.deposit')
        cust_deposit_product_obj = self.pool.get('cust.deposit.product')
        product_pricelist_item_obj = self.pool.get('product.pricelist.item')

        cust_deposit_product = cust_deposit_product_obj.browse(cr, uid, cust_deposit_product_id, context=context)
        cust_deposit = cust_deposit_obj.browse(cr, uid, cust_deposit_product.cust_deposit_id.id, context=context)

        if cust_deposit.pricelist_id.version_id[0].items_id:
            i = len(cust_deposit.pricelist_id.version_id[0].items_id) + 1
        else:
            i = 1
        version_id = cust_deposit.pricelist_id.version_id[0]
        vals = {}
        vals.update({'price_version_id': version_id.id})
        vals.update({'sequence': i})
        if cust_deposit_product.type == 'product':
            vals.update({'name': cust_deposit_product.product_id.name})
            vals.update({'product_id': cust_deposit_product.product_id.product_id.id})
        if cust_deposit_product.type == 'category':
            vals.update({'name': cust_deposit_product.product_category_id.name})
            vals.update({'categ_id': cust_deposit_product.product_category_id.id})
        if cust_deposit_product.type == 'merk':
            vals.update({'name': cust_deposit_product.product_merk_id.name})
            vals.update({'product_merk_id': cust_deposit_product.product_merk_id.id})
        vals.update({'base': 1})
        if cust_deposit_product.discount_type == 'amount':
            vals.update({'price_surcharge': cust_deposit_product.amount})
        else:
            if -100 <= cust_deposit_product.percentage <= 100:
                vals.update({'price_discount': cust_deposit_product.percentage / 100})
            else:
                raise osv.except_osv(_('Error!'), _('Percentage between -100 and 100!.'))

        res = product_pricelist_item_obj.create(cr, uid, vals, context=context)

    def _update_product_version(self, cr, uid, cust_deposit_product_id, context=None):
        #Get Pricelist -> Get Version -> Get Item match with product

        cust_deposit_obj = self.pool.get('cust.deposit')
        cust_deposit_product_obj = self.pool.get('cust.deposit.product')
        product_pricelist_item_obj = self.pool.get('product.pricelist.item')
        product_pricelist_version_obj = self.pool.get('product.pricelist.version')

        #Pricelist -> Pricelist Version -> Pricelist Item
        cust_deposit_product = cust_deposit_product_obj.browse(cr, uid, cust_deposit_product_id, context=context)
        cust_deposit = cust_deposit_obj.browse(cr, uid, cust_deposit_product.cust_deposit_id.id, context=context)
        priceslist_id = cust_deposit.pricelist_id
        version_id = priceslist_id.version_id[0]
        
        if cust_deposit_product.type == 'product':
            args = [('price_version_id','=',version_id.id),('product_tmpl_id','=', cust_deposit_product.product_id.id)]
        if cust_deposit_product.type == 'category':
            args = [('price_version_id','=',version_id.id),('categ_id','=', cust_deposit_product.product_category_id.id)]
        if cust_deposit_product.type == 'merk':
            args = [('price_version_id','=',version_id.id),('product_merk_id','=', cust_deposit_product.product_merk_id.id)]

        _logger.info(args)
        product_pricelist_item_ids  = product_pricelist_item_obj.search(cr, uid, args, context=None)
        if len(product_pricelist_item_ids) == 0:
            raise osv.except_osv(_('Error!'), _('Product item not found!.'))

        product_pricelist_item_id = product_pricelist_item_ids[0]
        
        vals = {}
        if cust_deposit_product.type == 'product':
            vals.update({'name': cust_deposit_product.product_id.name})
            vals.update({'product_id': cust_deposit_product.product_id.product_id.id})
        if cust_deposit_product.type == 'category':
            vals.update({'name': cust_deposit_product.product_category_id.name})
            vals.update({'categ_id': cust_deposit_product.product_category_id.id})
        if cust_deposit_product.type == 'merk':
            vals.update({'name': cust_deposit_product.product_merk_id.name})
            vals.update({'product_merk_id': cust_deposit_product.product_merk_id.id})
        vals.update({'base': 1})
        if cust_deposit_product.discount_type == 'amount':
            vals.update({'price_surcharge': cust_deposit_product.amount})
        else:
            if -100 <= cust_deposit_product.percentage <= 100:
                vals.update({'price_discount': cust_deposit_product.percentage / 100})
            else:
                raise osv.except_osv(_('Error!'), _('Percentage between -100 and 100!.'))

        res = product_pricelist_item_obj.write(cr, uid, [product_pricelist_item_id], vals, context=context)

    _columns = {
        'cust_deposit_id': fields.many2one('cust.deposit','Deposit #', readonly=True),
        'name': fields.char('Name', readonly=True),
        'type': fields.selection([('product','By Product'),('category','By Category'),('merk','By Merk')], 'Type', required=True),
        'product_id': fields.many2one('product.template', "Products"),
        'product_category_id': fields.many2one('product.category', "Product Category"),
        'product_merk_id': fields.many2one('product.merk','Product Merk'),
        'discount_type': fields.selection([('amount','Amount'),('percentage','Percentage')], 'Discount Type', default='amount'),
        'percentage': fields.float('Percentage'),
        'amount': fields.float('Amount'),
    }

    def create(self, cr, uid, vals, context=None):
        name = ''
        if vals.get('type') == 'product':
            name += 'By Product : ' + self._get_product(cr, uid, vals.get('product_id'), context=context).name
        if vals.get('type') == 'category':
            name += 'By Category : ' + self._get_product_category(cr, uid, vals.get('product_category_id'), context=context).name
        if vals.get('type') == 'merk':
            name += 'By Merk : ' + self._get_product_merk(cr, uid, vals.get('product_merk_id'), context=context).name
        vals.update({'name': name})
        
        res = super(jakc_cust_deposit_product, self).create(cr, uid, vals, context=context)
        self._add_product_version(cr, uid, res, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if 'type' in vals.keys():
            name = ''
            if vals.get('type') == 'product':
                name += 'By Product : ' + self._get_product(cr, uid, vals.get('product_id'), context=context).name
            if vals.get('type') == 'category':
                name += 'By Category : ' + self._get_product_category(cr, uid, vals.get('product_category_id'), context=context).name
            if vals.get('type') == 'merk':
                name += 'By Merk : ' + self._get_product_merk(cr, uid, vals.get('product_merk_id'), context=context).name
            vals.update({'name': name})

        res = super(jakc_cust_deposit_product, self).write(cr, uid, ids, vals, context=context)
        for cust_deposit_product in self.browse(cr, uid, ids, context=context):
            self._update_product_version(cr, uid, cust_deposit_product.id, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv(_('Access Denied!'), _('Cannot Deleted. Change amount to zero!'))

class jakc_cust_deposit_partner(osv.osv):
    _name = 'cust.deposit.partner'

    _columns = {
        'cust_deposit_id': fields.many2one('cust.deposit','Deposit #', readonly=True),
        'partner_id': fields.many2one('res.partner', "Partners"),
    }

class jakc_cust_deposit_payment(osv.osv):
    _name = 'cust.deposit.payment'

    def _get_company(self, cr, uid, context=None):
        return self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id

    def _get_deposit_journal(self, cr, uid, context=None):
        company_id = self._get_company(cr, uid, context=context)
        deposit_journal_id = company_id.deposit_journal_id
        return deposit_journal_id.id

    def _get_deposit_account(self, cr, uid, context=None):
        company_id = self._get_company(cr, uid, context=context)
        deposit_account_id = company_id.deposit_account_id
        return deposit_account_id.id

    def create_account_move(self, cr, uid, ids, context=None):

        payment = self.browse(cr, uid, ids[0], context=context)
        deposit = self.pool.get('cust.deposit').browse(cr, uid, payment.cust_deposit.id, context=context)
        company_id = self._get_company(cr, uid, context=context)

        l1 = {
            'name': deposit.partner_id.name + " Deposit",
            'debit': payment.amount,
            'credit': 0.0,
            'account_id': payment.account_id.id,
            'partner_id': deposit.partner_id.id,
            'ref': payment.name,
            'date': payment.trans_date,
            'company_id': company_id.id,
        }
        l2 = {
            'name': deposit.partner_id.name + " Deposit",
            'debit': 0.0,
            'credit': payment.amount,
            'account_id': payment.journal_id.default_credit_account_id.id,
            'partner_id': deposit.partner_id.id,
            'ref': payment.name,
            'date': payment.trans_date,
            'company_id': company_id.id,
        }


        move_vals = {
            'ref': payment.name,
            'line_id': [(0, 0, l1), (0, 0, l2)],
            'journal_id': payment.journal_id.id,
            'cust_deposit_id': deposit.id,
            'date': payment.trans_date,
            'narration': deposit.partner_id.name + " Deposit",
            'company_id': company_id.id,
        }

        move = self.pool.get('account.move').create(cr, uid, move_vals, context=context)

        if move:
            self.pool.get('account.move').post(cr, uid, move, context=context)
            super(jakc_cust_deposit_payment, self).write(cr, uid, ids, {'account_move_id':move,'iface_generated':True, 'state':'done'}, context=context)
        return True


    def trans_reopen(self, cr, uid, ids, context=None):
        payment = self.browse(cr, uid, ids[0], context=context)
        deposit = self.pool.get('cust.deposit').browse(cr, uid, payment.cust_deposit.id, context=context)
        company_id = self._get_company(cr, uid, context=context)
        if payment.account_move_id and payment.account_move_id.state == 'posted':
            raise osv.except_osv(_('Error!'), _('Please Cancel Journal Entry before Re-Open Payment!.'))
        else:
            #Delete Journal Entry
            super(jakc_cust_deposit_payment, self).write(cr, uid, ids, {'state': 'open'})

    _columns = {
        'cust_deposit': fields.many2one('cust.deposit', 'Deposit #', readonly=True),
        'name': fields.char('Trans #', size=50, readonly=True),
        'partner_id': fields.related('cust_deposit', 'partner_id', type='many2one', relation='res.partner', string='Partner', readonly=True),
        'trans_date': fields.date('Transaction Date', required=True),
        'journal_id': fields.many2one('account.journal', 'Journal', readonly=True),
        'account_id': fields.many2one('account.account', 'Bank or Check Account', required=True),
        'method_type': fields.selection(AVAILABLE_DEPOSIT, 'Method', size=16, required=True),
        'cheque_number': fields.char('Cheque #', size=50),
        'cheque_due_date': fields.date('Cheque Due Date'),
        'amount': fields.float('Amount', required=True),
        'account_move_id': fields.many2one('account.move', 'Journal Entry', readonly=True),
        'iface_generated': fields.boolean('Generated', readonly=True),
        'state': fields.selection(AVAILABLE_STATES, 'Status', size=16, readonly=True),
    }

    _defaults = {
        'state': 'open',
    }

    def create(self, cr, uid, vals, context=None):
        seq_obj = self.pool.get('ir.sequence')
        args = [('name', '=', 'Deposit')]
        seq_ids = seq_obj.search(cr, uid, args, context=context)
        name = seq_obj.next_by_id(cr, uid, seq_ids[0], context=context)
        vals.update({'name': name})
        company_id = self._get_company(cr, uid, context=context)
        vals.update({'journal_id': company_id.deposit_journal_id.id})
        return super(jakc_cust_deposit_payment, self).create(cr, uid, vals, context=context)

class product_pricelist(osv.osv):
    _inherit = 'product.pricelist'

    iface_deposit = fields.boolean('Is Deposit Priceslist')

