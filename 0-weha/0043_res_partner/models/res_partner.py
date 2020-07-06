from odoo import models, fields, api,  _ 
from odoo.exceptions import UserError, ValidationError
import logging


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    
    res_partner_payment_method_id = fields.Many2one('res.partner.payment.method')