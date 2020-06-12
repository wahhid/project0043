from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    merk_id = fields.Many2one(
        string='Merk',
        comodel_name='product.merk',
        ondelete='restrict',
    )

    warna = fields.Char('Color', size=50)
    
    motif = fields.Char(
        string='Motif',
        size=50,
    )

    page = fields.Char(
        string='Page',
        size=100,
    )
    
    size = fields.Char(
        string='Size',
        size=100
    )
    
    
    


