from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'


    def send_msg(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_user_id': self.id,
                            'default_model_id': 'res.partner'},
                }


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def send_msg(self):
        message  = ''
        message += " No Sale Order : {} ".format(self.name) + '%20'
        message += " Item : " + '%20'
        for line in self.order_line:
            message += " {} Qty {} Subtotal {}".format(line.product_id.name, line.product_uom_qty, line.product_uom_qty * line.price_unit) + '%20'
        
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_user_id': self.partner_id.id,
                            'default_message': message,  
                            'default_model_id': 'sale.order',  
                        },
                }