# -*- coding: utf-8 -*-

from odoo import fields, models,api
import json
import datetime
import io
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class AccountPartnerLedger(models.TransientModel):
    _name = "account.report.partner.ledger"

    partner_ids = fields.Many2many('res.partner', 'partner_ledger_partner_rel', 'id', 'partner_id', string='Partners')

    def pre_print_report(self, data):
        data['form'].update(self.read(['result_selection'])[0])
        return data

    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True,
                                   default=lambda self: self.env['account.journal'].search([]))
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')

    def _print_report(self, data):
        context = self._context
        data = self.pre_print_report(data)
        data['form'].update({'reconciled': self.reconciled, 'amount_currency': self.amount_currency,
                             'partner_ids': self.partner_ids.ids})

        if context.get('xls_export'):
            return {
                'type': 'ir_actions_xlsx_download',
                'data': {'model': 'account.report.partner.ledger',
                         'options': json.dumps(data, default=date_utils.json_default),
                         'output_format': 'xlsx',
                         'report_name': 'maintenance_report',
                         }
            }
            # return self.env.ref('account_reports_xlsx.partner_ledger_xlsx').report_action(self, data=data)
        else:
            return self.env.ref('account.action_report_partnerledger').report_action(self, data=data)

    amount_currency = fields.Boolean("With Currency",
                                     help="It adds the currency column on report if the currency differs from the company currency.")
    reconciled = fields.Boolean('Reconciled Entries')

    # def _print_report(self, data):
    #     data = self.pre_print_report(data)
    #     data['form'].update({'reconciled': self.reconciled, 'amount_currency': self.amount_currency})
    #     return self.env.ref('partner_report.action_report_partnerledger').report_action(self, data=data)
    #
    result_selection = fields.Selection([('customer', 'Receivable Accounts'),
                                         ('supplier', 'Payable Accounts'),
                                         ('customer_supplier', 'Receivable and Payable Accounts')
                                         ], string="Partner's", required=True, default='customer')



    def _build_contexts(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['strict_range'] = True if result['date_from'] else False
        return result

    # def _print_report(self, data):
    #     raise NotImplementedError()

    @api.multi
    def check_report_xlsx(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move'])[0]
        context = self._context
        data = self.pre_print_report(data)
        data['form'].update({'reconciled': self.reconciled, 'amount_currency': self.amount_currency,
                             'partner_ids': self.partner_ids.ids})
        # # ..........................
        # data = self.pre_print_report(data)
        # data['form'].update({'reconciled': self.reconciled, 'amount_currency': self.amount_currency})
        # # ...............................................................
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        # return self.with_context(discard_logo_check=True)._print_report(data)
        return {
            'type': 'ir_actions_xlsx_download',
            'data': {'model': 'account.report.partner.ledger',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'partner leger report',
                     }
                }

    def get_xlsx_report(self, options, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        data = {}
        data['form'] = options
        # data['form'] = vals.read([])[0]
        data['model'] = 'ir.ui.menu'
        data['ids'] = []
        data['form']['used_context'] = {}
        data['form']['used_context']['date_to'] = options['form']['date_to']
        data['form']['used_context']['date_from'] = options['form']['date_from']
        data['form']['used_context']['journal_ids'] = options['form']['journal_ids']
        data['form']['used_context']['state'] = 'posted'
        data['form']['used_context']['strict_range'] = True
        env_obj = self.search([('id','=',options['form']['id'])]).env['report.account.report_partnerledger']
        data['computed'] = {}
        obj_partner = env_obj.env['res.partner']
        query_get_data = env_obj.env['account.move.line'].with_context(
            data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']
        env_obj.env.cr.execute("""
                    SELECT a.id
                    FROM account_account a
                    WHERE a.internal_type IN %s
                    AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in env_obj.env.cr.fetchall()]
        params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        reconcile_clause = "" if data['form']['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        query = """
                    SELECT DISTINCT "account_move_line".partner_id
                    FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
                    WHERE "account_move_line".partner_id IS NOT NULL
                        AND "account_move_line".account_id = account.id
                        AND am.id = "account_move_line".move_id
                        AND am.state IN %s
                        AND "account_move_line".account_id IN %s
                        AND NOT account.deprecated
                        AND """ + query_get_data[1] + reconcile_clause
        env_obj.env.cr.execute(query, tuple(params))
        # # ---------------------Taking only selected partners---------------------------
        if data['form']['form']['partner_ids']:
            partner_ids = data['form']['form']['partner_ids']
        else:
            partner_ids = [res['partner_id'] for res in env_obj.env.cr.dictfetchall()]
        # # -----------------------------------------------------------------------------
        # partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]
        partners = obj_partner.browse(partner_ids)
        partners = sorted(partners, key=lambda x: (x.name or ''))
        # partners = sorted(partners, key=lambda x: (x.uniqueid or '', x.name or ''))
        for items in partners:
            partner_currency_balance = 0
            sheet = workbook.add_worksheet(str(items.name))
            format1 = workbook.add_format({'font_size': 16, 'align': 'center', 'bg_color': '#D3D3D3', 'bold': True})
            format1.set_font_color('#000080')
            format2 = workbook.add_format({'font_size': 12, 'bold': True})
            format3 = workbook.add_format({'font_size': 10, 'bold': True})
            format4 = workbook.add_format({'font_size': 10})
            format5 = workbook.add_format({'font_size': 10})
            format6 = workbook.add_format({'font_size': 10, 'bold': True})
            format7 = workbook.add_format({'font_size': 10, 'bold': True})
            format8 = workbook.add_format({'font_size': 10})
            format9 = workbook.add_format({'font_size': 10})
            format10 = workbook.add_format({'font_size': 10, 'bold': True})
            format1.set_align('center')
            format3.set_align('center')
            format4.set_align('center')
            format6.set_align('right')
            currency = self.env.user.company_id.currency_id.symbol
            format7.set_num_format('0.00 ' + currency)
            format8.set_num_format('0.00 ' + currency)
            logged_users = self.env['res.company']._company_default_get('account.account')
            sheet.merge_range('A1:B1', logged_users.name, format4)
            if data['form']['form']['date_from']:
                sheet.write('E2', 'Date from:', format6)
                sheet.write('F2', data['form']['form']['date_from'], format5)
            if data['form']['form']['date_to']:
                sheet.write('E3', 'Date to:', format6)
                sheet.write('F3', data['form']['form']['date_to'], format5)
            sheet.merge_range('I2:J2', 'Target Moves:', format6)
            if data['form']['form']['target_move'] == 'all':
                sheet.merge_range('K2:L2', 'All Entries', format4)
            if data['form']['form']['target_move'] == 'posted':
                sheet.merge_range('K2:L2', 'All Posted Entries', format4)
            sheet.merge_range(5, 0, 5, 1, "Date", format3)
            sheet.merge_range(5, 2, 5, 3, "JRNL", format3)
            sheet.merge_range(5, 4, 5, 5, "Account", format3)
            sheet.merge_range(5, 6, 5, 7, "Ref", format3)
            sheet.merge_range(5, 8, 5, 9, "Debit", format3)
            sheet.merge_range(5, 10, 5, 11, "Credit", format3)
            sheet.merge_range(5, 12, 5, 13, "Balance", format3)
            if data['form']['form']['amount_currency']:
                sheet.merge_range(5, 14, 5, 15, "Currency", format3)
                sheet.merge_range(3, 0, 4, 15, "Partner Ledger Report", format1)
            else:
                sheet.merge_range(3, 0, 4, 13, "Partner Ledger Report", format1)
            partner_name = ''
            # if items.uniqueid:
            #     partner_name = str(items.uniqueid)
            if items.name:
                partner_name = partner_name + str(items.name)
            sheet.merge_range(6, 0, 6, 6, partner_name, format2)
            debit = env_obj._sum_partner(data, items, 'debit')
            credit = env_obj._sum_partner(data, items, 'credit')
            balance = env_obj._sum_partner(data, items, 'debit - credit')
            sheet.merge_range(6, 8, 6, 9, debit, format7)
            sheet.merge_range(6, 10, 6, 11, credit, format7)
            sheet.merge_range(6, 12, 6, 13, balance, format7)
            row_value = 7
            for values in env_obj._lines(data, items):
                sheet.merge_range(row_value, 0, row_value, 1, values['date'], format4)
                sheet.merge_range(row_value, 2, row_value, 3, values['code'], format4)
                sheet.merge_range(row_value, 4, row_value, 5, values['a_code'], format4)
                sheet.merge_range(row_value, 6, row_value, 7, values['displayed_name'], format4)
                sheet.merge_range(row_value, 8, row_value, 9, values['debit'], format8)
                sheet.merge_range(row_value, 10, row_value, 11, values['credit'], format8)
                sheet.merge_range(row_value, 12, row_value, 13, values['progress'], format8)
                if data['form']['form']['amount_currency']:
                    if values['currency_id']:
                        partner_currency = values['currency_id'].symbol
                        format9.set_num_format('0.00 ' + partner_currency)
                        format10.set_num_format('0.00 ' + partner_currency)
                        sheet.merge_range(row_value, 14, row_value, 15, values['amount_currency'], format9)
                        partner_currency_balance += values['amount_currency']
                        sheet.merge_range(6, 14, 6, 15, partner_currency_balance, format10)
                row_value += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()