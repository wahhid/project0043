from odoo import models, fields, api,  _ 
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class ResPartnerPaymentMethod(models.Model):
    _name = "res.partner.payment.method"
    
    name = fields.Char('Name', size=100, required=True)
    
    