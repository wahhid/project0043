from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging


_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    
    has_courier = fields.Boolean('Has Courrier')
    
