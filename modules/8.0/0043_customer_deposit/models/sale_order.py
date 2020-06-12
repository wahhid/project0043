from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError, Warning
import logging


_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    #@api.onchange('pricelist_id')
    #def onchange_pricelist_id(self):
    #    self.recalculate_prices()


    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder,self).onchange_partner_id()
        cust_deposit_partner_ids = self.env['customer.deposit.partner'].search([('partner_id','=', self.partner_id.id)])
        if cust_deposit_partner_ids:
            values = {
                'show_deposit_option': True,
                'is_deposit': False,
                'cust_deposit_id': False,
            }
        else:
            values = {
                'show_deposit_option': False,
                'is_deposit': False,
                'cust_deposit_id': False,
            }
        
        self.update(values)
            #return {
            #    'warning': {'title':'Information', 'message':'Deposit available for this customer!',}
            #}
        

    @api.onchange('cust_deposit_id')
    def onchange_is_cust_deposit_id(self):
        for rec in self:   
            values = {
                'pricelist_id': rec.cust_deposit_id.pricelist_id.id or False,
            }
            self.update(values)
         
    
    @api.onchange('partner_id','is_deposit')
    def onchange_is_deposit(self):
        for rec in self:
            if rec.is_deposit:
                domain = [('is_deposit','=', rec.is_deposit),('partner_id','=', rec.partner_id.id)]
                #pricelist_id = self.env['product.pricelist'].search([('partner_id','=', rec.partner_id.id)], limit=1)
                #values = {
                #    'pricelist_id': pricelist_id.id or False,
                #}
                values = {
                    'pricelist_id': False,
                    'cust_deposit_id': False,
                }
                self.update(values)
            else:
                domain = []
                values = {
                    'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
                }
                self.update(values)
            return {'domain': {'pricelist_id': domain}}

    
    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({'sale_order_id': self.id})
        invoice_vals.update({'is_deposit': self.is_deposit})
        invoice_vals.update({'cust_deposit_id': self.cust_deposit_id.id})
        return invoice_vals


    show_deposit_option = fields.Boolean(
        string='Show Deposit Option',
        default= False,
    )
    
    is_deposit = fields.Boolean(
        string='Use Deposit',
        default = False,
    )

    
    cust_deposit_id = fields.Many2one(
        string='Deposit #',
        comodel_name='customer.deposit',
    )
    
    
    @api.one
    def trans_deposit(self):
        self.is_deposit = True

