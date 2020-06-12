from odoo import models, fields, api, _ 
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import logging


_logger = logging.getLogger(__name__)


class ReportSaleItemCust(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.0043_sale.sale_item_cust_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        date_start_obj = datetime.strptime(date_start, DATE_FORMAT)
        date_end_obj = datetime.strptime(date_end, DATE_FORMAT)
        date_diff = (date_end_obj - date_start_obj).days + 1

        #Get Distinct Partner
        sql = """SELECT distinct(a.partner_id), b.name
                 FROM account_invoice a 
                 LEFT JOIN res_partner b ON a.partner_id = b.id
                 WHERE a.date_invoice>='%s' AND a.date_invoice<='%s' AND a.type='out_invoice'
              """ % (date_start_obj.strftime(DATETIME_FORMAT),  date_end_obj.strftime(DATETIME_FORMAT))
        
        _logger.info(sql)
        self.env.cr.execute(sql)
        partners = self.env.cr.fetchall()
        docs = []
        for partner in partners:
            vals = {}
            vals.update({
                'partner_id': partner[0],
                'partner_name': partner[1],
            })
            #Get Invoice 
            sql = """SELECT a.id, a.number, a.date_invoice, a.amount_total
                     FROM account_invoice a 
                     WHERE a.partner_id = %s
                  """ % (partner[0])
            self.env.cr.execute(sql)
            invoices = self.env.cr.fetchall()
            invoice_ids = []
            for invoice in invoices:
                invoice_vals = {
                    'id': invoice[0],
                    'number': invoice[1],
                    'date_invoice': invoice[2],
                    'amount_total': invoice[3],
                }
                #Get Invoice Line
                sql = """SELECT c.default_code, d.name as product_name, 
                                e.name as merk_name,  f.name as uom_name , 
                                a.quantity, a.price_subtotal
                            FROM account_invoice_line a
                            LEFT JOIN account_invoice b ON a.invoice_id = b.id
                            LEFT JOIN product_product c ON a.product_id = c.id 
                            LEFT JOIN product_template d ON c.product_tmpl_id = d.id
                            LEFT JOIN product_merk e ON d.merk_id = e.id
                            LEFT JOIN uom_uom f ON d.uom_id = f.id
                            WHERE  a.invoice_id = %s""" % (invoice[0])
                self.env.cr.execute(sql)
                invoice_lines = self.env.cr.fetchall()
                lines = []
                for line in invoice_lines:
                    line_vals = {
                        'default_code': line[0],
                        'product_name': line[1],
                        'merk_name': line[2],
                        'uom_name': line[3],
                        'quantity': line[4],
                        'price_subtotal': line[5],
                    }
                    lines.append(line_vals)
                invoice_vals.update({
                    'line_count': len(lines),
                    'lines': lines
                })
                invoice_ids.append(invoice_vals)
            vals.update({'invoice_ids': invoice_ids})
            docs.append(vals)
            
        _logger.info(docs)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'company': self.env.user.company_id,
            'docs': docs,
        }



