import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


    @api.model
    def default_get(self, fields):
        res = super(AccountInvoice, self).default_get(fields)
        company_id = self.env.user.company_id
        res.update({'other_info_row1': company_id.other_info_row1})
        res.update({'other_info_row2': company_id.other_info_row2})
        res.update({'other_info_row3': company_id.other_info_row3})
        res.update({'other_info_row4': company_id.other_info_row4})
        return res


    @api.one
    def get_other_info(self):
        str = ''
        if self.other_info_row1:
            str = str + self.other_info_row1 + '\n'

        if self.other_info_row2:
            str = str + self.other_info_row2 + '\n'

        if self.other_info_row3:
            str = str + self.other_info_row3 + '\n'

        if self.other_info_row4:
            str = str + self.other_info_row4 + '\n'

        self.other_info = str

    @api.one
    def get_show_print_button(self):
        return True

    @api.one
    def get_courier_from_picking(self):
        if len(self.picking_ids) > 0:
            self.courier = self.picking_ids[0].courier

    courier = fields.Char('Courier', compute='get_courier_from_picking', readonly=True)
    other_info = fields.Text('Other Information', compute='get_other_info', readonly=True)
    other_info_row1 = fields.Char('Row 1', size=100)
    other_info_row2 = fields.Char('Row 2', size=100)
    other_info_row3 = fields.Char('Row 3', size=100)
    other_info_row4 = fields.Char('Row 4', size=100)

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        account_invoice_obj = self.env['account.invoice']
        account_invoice_obj.add_print_count(self)
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        self.sent = True
        return self.env['report'].get_action(self, 'jakc_account_invoice_report.report_account_invoice')