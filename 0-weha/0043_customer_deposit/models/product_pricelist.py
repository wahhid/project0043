from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_repr
from odoo.addons import decimal_precision as dp
from odoo.tools import pycompat
import logging


_logger = logging.getLogger(__name__)

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'


    is_deposit = fields.Boolean(
        string='Is Deposit',
        default = False,
    )

    
    partner_id = fields.Many2one(
        string='Partner Deposit',
        comodel_name='res.partner',
    )
    

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    @api.one
    @api.depends('categ_id', 'product_tmpl_id', 'product_id', 'merk_id', 'compute_price', 'fixed_price', \
        'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge')
    def _get_pricelist_item_name_price(self):
        if self.categ_id:
            self.name = _("Category: %s") % (self.categ_id.name)
        elif self.product_tmpl_id:
            self.name = self.product_tmpl_id.name
        elif self.product_id:
            self.name = self.product_id.display_name.replace('[%s]' % self.product_id.code, '')
        elif self.merk_id:
            self.name = _("Merk: %s") % (self.merk_id.name)
        else:
            self.name = _("All Products")

        if self.compute_price == 'fixed':
            self.price = ("%s %s") % (
                float_repr(
                    self.fixed_price,
                    self.pricelist_id.currency_id.decimal_places,
                ),
                self.pricelist_id.currency_id.name
            )
        elif self.compute_price == 'percentage':
            self.price = _("%s %% discount") % (self.percent_price)
        else:
            self.price = _("%s %% discount and %s surcharge") % (self.price_discount, self.price_surcharge)

    @api.onchange('applied_on')
    def _onchange_applied_on(self):
        if self.applied_on != '0_product_variant':
            self.product_id = False
        if self.applied_on != '1_product':
            self.product_tmpl_id = False
        if self.applied_on != '2_product_category':
            self.categ_id = False
        if self.applied_on != '4_merk':
            self.merk_id = False

    applied_on = fields.Selection(selection_add=[('4_merk', 'Merk')])
    
    merk_id = fields.Many2one(
        string='Merk',
        comodel_name='product.merk',
        ondelete='cascade'
    )
    
    cust_deposit_product_id = fields.Many2one(
        string='Deposit Product #',
        comodel_name='customer.deposit.product',
    )
    

