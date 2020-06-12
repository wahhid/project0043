from datetime import datetime
import pytz
import time
from openerp import tools
from openerp.osv import osv
from openerp.report import report_sxw
import logging

_logger = logging.getLogger(__name__)


class account_invoice_per_item(report_sxw.rml_parse):

    def _get_account_invoice_periode(self, form):
        account_voucher_obj = self.pool.get('account.invoice')
        user_obj = self.pool.get('res.users')
        data = []
        result = {}
        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        date_start = form['date_start']
        date_end = form['date_end']

        #account_invoice_ids = account_invoice_obj.search(self.cr, self.uid, [
        #    ('date', '>=', date_start),
        #    ('date', '<', date_end),
        #    ('state', 'in', ['posted']),
        #    ('type','=', form['type']),
        #    ('company_id', '=', company_id)
        #])

        strSQL = """
                    SELECT c.default_code, d.name as product, e.name as uom, SUM(a.quantity) as quantity, SUM(a.price_subtotal) as price_subtotal FROM account_invoice_line as a
                    LEFT JOIN account_invoice b on a.account_id = b.id
                    LEFT JOIN product_product c on a.product_id = c.id
                    LEFT JOIN product_template d on c.product_tmpl_id = d.id
                    LEFT JOIN product_uom e on a.uos_id = e.id
                    WHERE date_invoice BETWEEN '{}' AND '{}'
                    GROUP BY c.default_code, d.name, e.name
                    ORDER BY d.name
                """.format(date_start, date_end)
        self.cr.execute(strSQL)
        rows = self.cr.dictfetchall()        
        for row in rows:
            result = {
                'default_code': row.get('default_code'),
                'product': row.get('product'),
                'uom': row.get('uom'),
                'quantity': row.get('quantity'),
                'price_subtotal':  row.get('price_subtotal'),
            } 
            data.append(result)
        return data

    def __init__(self, cr, uid, name, context):
        super(account_invoice_per_item, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'datetime': datetime,
            'get_account_invoice':self._get_account_invoice_periode,
        })


class report_account_invoice_payment_periode(osv.AbstractModel):
    _name = 'report.jakc_account_invoice_report.report_accountinvoiceperitemperiode'
    _inherit = 'report.abstract_report'
    _template = 'jakc_account_invoice_report.report_accountinvoiceperitemperiode'
    _wrapped_report_class = account_invoice_per_item