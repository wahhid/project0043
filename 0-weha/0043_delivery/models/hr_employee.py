from odoo import models, fields, api 
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_courier = fields.Boolean('Is Courier')
