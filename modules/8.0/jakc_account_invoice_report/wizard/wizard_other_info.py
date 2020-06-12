from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, Warning


class WizardOtherInfo(models.Model):
    _name = 'wizard.other.info'

    @api.model
    def default_get(self, fields):
        res = super(WizardOtherInfo, self).default_get(fields)
        active_id = self.env.context.get('active_id') or False
        inv = self.env['account.invoice'].browse(active_id)
        res.update({'other_info_row1': inv.other_info_row1})
        res.update({'other_info_row2': inv.other_info_row2})
        res.update({'other_info_row3': inv.other_info_row3})
        res.update({'other_info_row4': inv.other_info_row4})
        return res

    other_info_row1 = fields.Char('Row 1', size=100)
    other_info_row2 = fields.Char('Row 2', size=100)
    other_info_row3 = fields.Char('Row 3', size=100)
    other_info_row4 = fields.Char('Row 4', size=100)

    @api.one
    def process(self):
        active_id = self.env.context.get('active_id') or False
        account_invoice_obj = self.env['account.invoice']
        inv = account_invoice_obj.browse(active_id)
        if inv:
            inv.other_info_row1 = self.other_info_row1
            inv.other_info_row2 = self.other_info_row2
            inv.other_info_row3 = self.other_info_row3
            inv.other_info_row4 = self.other_info_row4




