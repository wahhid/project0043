from odoo import models, fields, api, _ 
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
import logging


_logger = logging.getLogger(__name__)


class SaleItemReportWizard(models.TransientModel):
    _name = 'sale.item.report.wizard'

    @api.onchange('report_type')
    def _onchange_report_type(self):
        if self.report_type != 'net':
            self.merk_ids = False
        else:
            self.merk_ids = self.env['product.merk'].search([])


    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)
    merk_ids = fields.Many2many(
        string='Merk/Catalog',
        comodel_name='product.merk',
        required=True,
    )
    report_type = fields.Selection(
        string='Type',
        selection=[('jual', 'Jual'), ('retur', 'Retur'),('net','Net')],
        default='jual',
        required=True,
    )

    @api.multi
    def get_report(self):
        _logger.info(self.merk_ids.ids)
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'merk_ids': self.merk_ids.ids,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
        if self.report_type == 'jual':
            return self.env.ref('0043_sale.sale_item_report').report_action(self, data=data)
        else:
            return self.env.ref('0043_sale.sale_retur_item_report').report_action(self, data=data)

