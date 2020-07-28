import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    @api.one
    def add_print_count(self):
        self.printed_number = self.printed_number + 1

    @api.one
    def add_print_checking_count(self):
        self.printed_checking = self.printed_checking + 1

    @api.one
    def add_print_dropshipping_count(self):
        self.printed_dropshipping = self.printed_dropshipping + 1

    courier = fields.Char('Courier', size=100)
    printed_number = fields.Integer('Print #', default=0)
    printed_checking = fields.Integer('Print Checking #', default=0)
    printed_dropshipping = fields.Integer('Print Dropshipping #', default=0)


    @api.multi
    def trans_print_checking(self):
        self.add_print_checking_count()
        return self.env['report'].get_action(self, 'jakc_stock_report.report_picking_custom_checking')

    @api.multi
    def trans_print_do(self):
        self.add_print_count()
        return self.env['report'].get_action(self, 'jakc_stock_report.report_picking_custom')

    @api.multi
    def trans_print_dropshipping(self):
        self.add_print_dropshipping_count()
        return self.env['report'].get_action(self, 'jakc_stock_report.report_picking_custom_dropshipping')
