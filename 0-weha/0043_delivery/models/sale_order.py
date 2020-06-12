from odoo import models, fields, api 
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    courier_id = fields.Many2one('hr.employee','Courier')
