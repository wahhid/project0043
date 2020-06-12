from odoo import models, api, fields, _ 
from odoo.exceptions import UserError, ValidationError


class ProductMerk(models.Model):
    _name = 'product.merk'

    name = fields.Char("Merk", size=250,required=True)
