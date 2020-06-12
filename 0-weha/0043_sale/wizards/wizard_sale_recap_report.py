from odoo import models, fields, api, _ 
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
import logging


_logger = logging.getLogger(__name__)


class SaleRecapReportWizard(models.TransientModel):
    _name = 'sale.recap.report.wizard'

    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)
    report_type = fields.Selection(
        string='Type',
        selection=[('rekap', 'Rekap'), ('detail', 'Detail'),],
        default='rekap',
        required=True,
    )
    
    @api.multi
    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.
        if self.report_type == 'rekap':
            return self.env.ref('0043_sale.sale_recap_report').report_action(self, data=data)
        else:
            return self.env.ref('0043_sale.sale_detail_recap_report').report_action(self, data=data)


