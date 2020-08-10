from odoo import models, fields, api, _ 
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.tools import formatLang
import logging


_logger = logging.getLogger(__name__)


class ReportSaleReturRecap(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.0043_sale.sale_retur_recap_report_view'

    def convert_2float(self, value, precision=2, currency_obj=None, context=None):
        fmt = '%f' if precision is None else '%.{precision}f'
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        formatted = formatLang(self.env, value, currency_obj=currency_obj)
        return formatted
    
    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        date_start_obj = datetime.strptime(date_start, DATE_FORMAT)
        date_end_obj = datetime.strptime(date_end, DATE_FORMAT)
        date_diff = (date_end_obj - date_start_obj).days + 1

        docs = []
        invoices = self.env['account.invoice'].search([
            ('date_invoice', '>=', date_start_obj.strftime(DATETIME_FORMAT)),
            ('date_invoice', '<=', date_end_obj.strftime(DATETIME_FORMAT)),
            ('type','=','out_refund'),
            ], order='date_invoice asc')
            
        for invoice in invoices:
            docs.append({
                'number': invoice.number,
                'date_invoice': invoice.date_invoice,
                'partner_name': invoice.partner_id.name, 
                'amount_total': invoice.amount_total,
            })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start_obj.strftime("%d-%m-%Y"),
            'date_end': date_end_obj.strftime("%d-%m-%Y"),
            'currency': self.env.user.company_id.currency_id,
            'convert_2float': self.convert_2float,
            'docs': docs,
        }

class ReportSaleReturDetailRecap(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.0043_sale.sale_retur_detail_recap_report_view'
    
    
    def convert_2float(self, value, precision=2, currency_obj=None, context=None):
        fmt = '%f' if precision is None else '%.{precision}f'
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        formatted = formatLang(self.env, value, currency_obj=currency_obj)
        return formatted

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        date_start_obj = datetime.strptime(date_start, DATE_FORMAT)
        date_end_obj = datetime.strptime(date_end, DATE_FORMAT)
        date_diff = (date_end_obj - date_start_obj).days + 1

        docs = []
        invoices = self.env['account.invoice'].search([
            ('date_invoice', '>=', date_start_obj.strftime(DATETIME_FORMAT)),
            ('date_invoice', '<=', date_end_obj.strftime(DATETIME_FORMAT)),
            ('type','=','out_refund'),
            ], order='date_invoice asc')
            
        for invoice in invoices:
            lines = []
            for line in invoice.invoice_line_ids:
                lines.append({
                    'product_name': line.product_id.name,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                })
            docs.append({
                'number': invoice.number,
                'date_invoice': invoice.date_invoice,
                'partner_name': invoice.partner_id.name, 
                'amount_total': invoice.amount_total,
                'lines': lines,
            })

        _logger.info(docs)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start_obj.strftime("%d-%m-%Y"),
            'date_end': date_end_obj.strftime("%d-%m-%Y"),
            'currency': self.env.user.company_id.currency_id,
            'convert_2float': self.convert_2float,
            'docs': docs,
        }