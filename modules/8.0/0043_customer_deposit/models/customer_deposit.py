from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
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

class CustomerDeposit(models.Model):
    _name = 'customer.deposit'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.one
    def trans_confirm(self):
        #cust_deposit_obj = self.pool.get('cust.deposit')
        #deposit = self.browse(cr, uid, ids, context=context)[0]
        #pricelist_id = deposit.pricelist_id
        #version_id = pricelist_id.version_id[0]
        #self._generate_public_pricelist(cr, uid, version_id.id, context=context)
        self.write({'state': 'open'})


    @api.one
    def calculate_rest_amount(self):
        result = {}
        #company_id = self._get_company(cr, uid, context=context)
        #if not company_id.deposit_journal_id:
        #    raise osv.except_osv(_('Error!'), _('Please define default deposit journal for the company.'))
        Params = self.env['ir.config_parameter'].sudo()
        customer_deposit_account_id = Params.get_param('0043_customer_deposit.customer_deposit_account_id') or False

        for deposit in self:
            if not customer_deposit_account_id:
                result[deposit.id] = 0
            else:    
                for deposit in self:
                    sql = """SELECT sum(a.credit - a.debit) as rest_amount
                                        FROM account_move_line a
                                        INNER JOIN account_move b ON a.move_id = b.id
                                        WHERE b.cust_deposit_id=%s AND a.account_id=%s"""

                    self.env.cr.execute(sql, (deposit.id, customer_deposit_account_id))
                    result[deposit.id] = self.env.cr.fetchone()[0]
    
            
    def auto_create_pricelist(self):
        pricelist_obj = self.env['product.pricelist']
        pricelist_item_obj = self.env['product.pricelist.item']
        pricelist_vals = {
            'partner_id': self.partner_id.id,
            'name': 'Pricelist - ' + self.partner_id.name,
            'type': 'sale',
            'is_deposit': True
        }
        pricelist_id = pricelist_obj.create(pricelist_vals)
        super(CustomerDeposit, self).write({'pricelist_id': pricelist_id.id})


    name = fields.Char('Name', size=50)
    trans_number = fields.Char('', size=20, readonly=True)
    trans_date = fields.Date('Transaction Date', default=fields.Date.context_today, required=True)
    partner_id = fields.Many2one('res.partner','Partner  # ', required=True)
    pricelist_id = fields.Many2one('product.pricelist','Pricelist', readonly=True)
    iface_generated = fields.Boolean('Generated', readonly=True)
    rest_amount = fields.Float(string='Rest Amount', compute="calculate_rest_amount")
    payment_ids = fields.One2many('customer.deposit.payment', 'cust_deposit_id', 'Payments')
    product_ids = fields.One2many('customer.deposit.product', 'cust_deposit_id', 'Products')
    partner_ids = fields.One2many('customer.deposit.partner', 'cust_deposit_id', 'Partners')
    account_move_ids = fields.One2many('account.move', 'cust_deposit_id', 'Moves')
    state = fields.Selection(AVAILABLE_STATES, 'Status', default='draft', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('trans_number', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['trans_number'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('customer.deposit') or _('New')
            else:
                vals['trans_number'] = self.env['ir.sequence'].next_by_code('customer.deposit') or _('New')
        #trans_number = datetime.now().strftime('%Y%m%d%H%M%S')
        #vals.update({'trans_number': trans_number})
        res = super(CustomerDeposit, self).create(vals)
        res.auto_create_pricelist()
        return res


class CustomerDepositPayment(models.Model):
    _name = 'customer.deposit.payment'

    @api.one
    def trans_reopen(self):
        payment = self
        deposit = payment.cust_deposit_id
        company_id = self.env.user.company_id
        if payment.account_move_id and payment.account_move_id.state == 'posted':
            raise ValidationError(_('Error!'), _('Please Cancel Journal Entry before Re-Open Payment!.'))
        else:
            #Delete Journal Entry
            if payment.account_move_id:
                self.env['account.move'].unlink(payment.account_move_id.id)
            super(CustomerDepositPayment, self).write({'state': 'open','iface_generated': False})


    def create_account_move(self):

        for payment in self:
            deposit = payment.cust_deposit_id
            company_id = self.env.user.company_id 

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
                'line_ids': [(0, 0, l1), (0, 0, l2)],
                'journal_id': payment.journal_id.id,
                'cust_deposit_id': deposit.id,
                'date': payment.trans_date,
                'narration': deposit.partner_id.name + " Deposit",
                'company_id': company_id.id,
            }

            move = self.env['account.move'].create(move_vals)
            if move:
                super(CustomerDepositPayment, self).write({'account_move_id':move.id,'iface_generated':True, 'state':'done'})
                Params = self.env['ir.config_parameter'].sudo()
                is_auto_posted = Params.get_param('0043_customer_deposit.is_auto_posted')
                if is_auto_posted:
                    move.action_post()

        return True


    cust_deposit_id = fields.Many2one('customer.deposit', 'Deposit #', readonly=True)
    name = fields.Char('Trans #', size=50, readonly=True)
    nickname = fields.Char(related='cust_deposit_id.partner_id.name', store=True)
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    trans_date = fields.Date('Transaction Date', required=True)
    journal_id = fields.Many2one('account.journal', 'Journal', readonly=True)
    account_id = fields.Many2one('account.account', 'Bank or Check Account', required=True)
    method_type = fields.Selection(AVAILABLE_DEPOSIT, 'Method', size=16, required=True)
    cheque_number = fields.Char('Cheque #', size=50)
    cheque_due_date = fields.Date('Cheque Due Date')
    amount = fields.Float('Amount', required=True)
    account_move_id = fields.Many2one('account.move', 'Journal Entry', readonly=True)
    iface_generated = fields.Boolean('Generated', readonly=True)
    state = fields.Selection(AVAILABLE_STATES, 'Status', size=16, default='open', readonly=True)

    @api.model 
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('customer.deposit.payment') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('customer.deposit.payment') or _('New')
        
        Params = self.env['ir.config_parameter'].sudo()
        customer_deposit_journal_id = Params.get_param('0043_customer_deposit.customer_deposit_journal_id') or False
        _logger.info(customer_deposit_journal_id)
        vals['journal_id'] = customer_deposit_journal_id

        res = super(CustomerDepositPayment, self).create(vals)
        return res 


class CustomerDepositPartner(models.Model):
    _name = 'customer.deposit.partner'

    cust_deposit_id = fields.Many2one('customer.deposit','Deposit #', readonly=True)
    partner_id = fields.Many2one('res.partner', "Partners", required=True)

    _sql_constraints = [ ('unique_deposit_partner', 'unique(cust_deposit_id, partner_id)', 'Partner already exsist\n Please, select a different partner')	]


class CustomerDepositProduct(models.Model):
    _name = 'customer.deposit.product'

    def add_product(self):
        vals = {}
        vals.update({'pricelist_id': self.cust_deposit_id.pricelist_id.id})
        vals.update({'cust_deposit_product_id': self.id})
        if self.type == 'product':
            vals.update({'applied_on': '1_product'})
            #vals.update({'name': self.product_id.name})
            vals.update({'product_tmpl_id': self.product_id.id})
        if self.type == 'category':
            vals.update({'applied_on': '2_product_category'})
            #vals.update({'name': self.product_category_id.name})
            vals.update({'categ_id': self.product_category_id.id})
        if self.type == 'merk':
            vals.update({'applied_on': '4_merk'})
            #vals.update({'name': self.product_merk_id.name})
            vals.update({'merk_id': self.product_merk_id.id})
        
        vals.update({'base': 'list_price'})
        vals.update({'compute_price': 'formula'})
        
        if self.discount_type == 'amount':
            vals.update({'price_surcharge': self.amount})
        else:
            if -100 <= self.percentage <= 100:
                vals.update({'price_discount': self.percentage / 100})
            else:
                raise ValidationError(_('Error!'), _('Percentage between -100 and 100!.'))

        res = self.env['product.pricelist.item'].create(vals)

    def update_product(self):
        item = self.env['product.pricelist.item'].search({'cust_deposit_product_id': self.id})
        if not item:
            raise ValidationError(_('Error!'), _('Product Pricelist Item not found'))

        vals = {}
        if self.type == 'product':
            vals.update({'name': self.product_id.name})
            vals.update({'product_id': self.product_id.id})
        if self.type == 'category':
            vals.update({'name': self.product_category_id.name})
            vals.update({'categ_id': self.product_category_id.id})
        if self.type == 'merk':
            vals.update({'name': self.product_merk_id.name})
            vals.update({'product_merk_id': self.product_merk_id.id})
        
        vals.update({'base': 'list_price'})

        if self.discount_type == 'amount':
            vals.update({'price_surcharge': self.amount})
        else:
            if -100 <= self.percentage <= 100:
                vals.update({'price_discount': self.percentage / 100})
            else:
                raise ValidationError(_('Error!'), _('Percentage between -100 and 100!.'))

        super(CustomerDepositProduct, self).write(vals)


    @api.one
    @api.depends('product_id', 'product_category_id', 'product_merk_id', 'type')
    def _get_product_deposit_name(self):
        if self.product_category_id:
            self.name = _("Category: %s") % (self.product_category_id.name)
        elif self.product_id:
            self.name = self.product_id.name
        elif self.product_merk_id:
            self.name = _("Merk: %s") % (self.product_merk_id.name)
        else:
            self.name = ''

    @api.onchange('type')
    def _onchange_applied_on(self):
        if self.type != 'product':
            self.product_id = False
        if self.type != 'category':
            self.product_category_id = False
        if self.type != 'merk':
            self.product_merk_id = False


    cust_deposit_id = fields.Many2one('customer.deposit','Deposit #', readonly=True)
    name = fields.Char('Name', compute='_get_product_deposit_name', readonly=True)
    type = fields.Selection([('product','By Product'),('category','By Category'),('merk','By Merk')], 'Type', default='product', required=True)
    product_id = fields.Many2one('product.template', "Products")
    product_category_id = fields.Many2one('product.category', "Product Category")
    product_merk_id = fields.Many2one('product.merk','Product Merk')
    discount_type = fields.Selection([('amount','Amount'),('percentage','Percentage')], 'Discount Type', default='amount')
    percentage = fields.Float('Percentage')
    amount = fields.Float('Amount')

    @api.model
    def create(self, vals):        
        res = super(CustomerDepositProduct, self).create(vals)
        res.add_product()
        return res

    @api.multi
    def write(self, vals):        
        res = super(CustomerDepositProduct, self).write(vals)
        res.update_product()
        return res


    @api.multi 
    def unlink(self):
        item = self.env['product.pricelist.item'].search([('cust_deposit_product_id', '=', self.id)])
        if item:
            item.unlink()
        super(CustomerDepositProduct, self).unlink()
