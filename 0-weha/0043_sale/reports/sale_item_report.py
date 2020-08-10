from odoo import models, fields, api, _ 
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import logging


_logger = logging.getLogger(__name__)


class ReportSaleItem(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.0043_sale.sale_item_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        merk_ids = data['form']['merk_ids']
        date_start_obj = datetime.strptime(date_start, DATE_FORMAT)
        date_end_obj = datetime.strptime(date_end, DATE_FORMAT)
        date_diff = (date_end_obj - date_start_obj).days + 1
        
        if len(merk_ids) == 1:
            merks = "(" + str(merk_ids[0]) + ")"
        else:
            merks = tuple(merk_ids)

        sql = """SELECT c.default_code, d.name as product_name, 
                        e.name as merk_name, d.size, sum(a.quantity) as total_item
                    FROM account_invoice_line a
                    LEFT JOIN account_invoice b ON a.invoice_id = b.id
                    LEFT JOIN product_product c ON a.product_id = c.id 
                    LEFT JOIN product_template d ON c.product_tmpl_id = d.id
                    LEFT JOIN product_merk e ON d.merk_id = e.id
                    WHERE b.date_invoice>='%s' AND b.date_invoice<='%s' AND d.merk_id in %s AND b.type='out_invoice'
                    GROUP BY c.default_code, d.name, e.name, d.size
                    ORDER BY c.default_code""" % (date_start_obj.strftime(DATETIME_FORMAT),  date_end_obj.strftime(DATETIME_FORMAT), merks)
                    
        _logger.info(sql)
        self.env.cr.execute(sql)
        records = self.env.cr.fetchall()
        docs = []
        for record in records:
            docs.append({
                'default_code': record[0],
                'product_name': record[1],
                'merk_name': record[2], 
                'size': record[3],
                'total_item': record[4],
            })
            
        _logger.info(docs)


        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start_obj.strftime("%d-%m-%Y"),
            'date_end': date_end_obj.strftime("%d-%m-%Y"),
            'docs': docs,
        }


class ReportSaleReturItem(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.0043_sale.sale_retur_item_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        date_start_obj = datetime.strptime(date_start, DATE_FORMAT)
        date_end_obj = datetime.strptime(date_end, DATE_FORMAT)
        date_diff = (date_end_obj - date_start_obj).days + 1

        if len(merk_ids) == 1:
                merks = "(" + str(merk_ids[0]) + ")"
        else:
            merks = tuple(merk_ids)
            
        sql = """SELECT c.default_code, d.name as product_name, 
                        e.name as merk_name, d.size, sum(a.quantity) as total_item
                    FROM account_invoice_line a
                    LEFT JOIN account_invoice b ON a.invoice_id = b.id
                    LEFT JOIN product_product c ON a.product_id = c.id 
                    LEFT JOIN product_template d ON c.product_tmpl_id = d.id
                    LEFT JOIN product_merk e ON d.merk_id = e.id
                    WHERE b.date_invoice>='%s' AND b.date_invoice<='%s' AND b.type='out_refund' AND d.merk_id in %s
                    GROUP BY c.default_code, d.name, e.name, d.size
                    ORDER BY c.default_code""" % (date_start_obj.strftime(DATETIME_FORMAT),  date_end_obj.strftime(DATETIME_FORMAT), merks)
                    
        _logger.info(sql)
        self.env.cr.execute(sql)
        records = self.env.cr.fetchall()
        docs = []
        for record in records:
            docs.append({
                'default_code': record[0],
                'product_name': record[1],
                'merk_name': record[2], 
                'size': record[3],
                'total_item': record[4],
            })
            
        _logger.info(docs)


        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start_obj.strftime("%d-%m-%Y"),
            'date_end': date_end_obj.strftime("%d-%m-%Y"),
            'docs': docs,
        }

