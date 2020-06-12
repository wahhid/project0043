# -*- coding: utf-8 -*-

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import json
import datetime
import io
from odoo import api, fields, models, _
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class AccountAgedTrialBalance(models.TransientModel):

    _name = 'account.aged.trial.balance'
    _description = 'Account Aged Trial balance Report'

    period_length = fields.Integer(string='Period Length (days)', required=True, default=30)
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True)
    date_from = fields.Date(default=lambda *a: time.strftime('%Y-%m-%d'))

    def _print_report(self, data):
        res = {}
        data = self.pre_print_report(data)
        data['form'].update(self.read(['period_length'])[0])
        period_length = data['form']['period_length']
        if period_length<=0:
            raise UserError(_('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise UserError(_('You must set a start date.'))

        start = datetime.strptime(str(data['form']['date_from']), "%Y-%m-%d")

        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length - 1)
            res[str(i)] = {
                'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
        data['form'].update(res)
        return self.env.ref('account.action_report_aged_partner_balance').with_context(landscape=True).report_action(self, data=data)

    def pre_print_report(self, data):
        data['form'].update(self.read(['result_selection'])[0])
        return data

    result_selection = fields.Selection([('customer', 'Receivable Accounts'),
                                         ('supplier', 'Payable Accounts'),
                                         ('customer_supplier', 'Receivable and Payable Accounts')
                                         ], string="Partner's", required=True, default='customer')



    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True,
                                   default=lambda self: self.env['account.journal'].search([]))
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')

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
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        return {
            'type': 'ir_actions_xlsx_download',
            'data': {'model': 'account.aged.trial.balance',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'aged partner report',
                     }
        }

    def get_xlsx_report(self, options, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        env_obj = self.search([('id','=',options['form']['id'])]).env['report.account.report_agedpartnerbalance']
        vals = self.search([('id','=',options['form']['id'])])
        result_selection = vals.result_selection
        if result_selection == 'customer':
            account_type = ['receivable']
            account_type_name = "Receivable Accounts"
        elif result_selection == 'supplier':
            account_type = ['payable']
            account_type_name = "Payable Accounts"
        else:
            account_type = ['payable', 'receivable']
            account_type_name = "Receivable and Payable Accounts"
        # sales_person_wise = vals.user_wise_report
        date_from = options['form']['date_from']
        target_move = options['form']['target_move']
        if target_move == 'all':
            target_move_name = "All Entries"
        else:
            target_move_name = "All Posted Entries"
        period_length = vals.period_length
        # # user_ids = vals.user_ids.ids
        move_lines, total, dummy = env_obj._get_partner_move_lines(account_type, date_from, target_move, period_length)
        sheet = workbook.add_worksheet()
        format1 = workbook.add_format({'font_size': 16, 'align': 'center', 'bg_color': '#D3D3D3', 'bold': True})
        format1.set_font_color('#000080')
        format2 = workbook.add_format({'font_size': 10, 'bold': True})
        format3 = workbook.add_format({'font_size': 10})
        logged_users = self.env['res.company']._company_default_get('account.account')
        sheet.write('A1', logged_users.name, format3)
        sheet.write('A3', 'Start Date:', format2)
        sheet.write('B3', date_from, format3)
        sheet.merge_range('E3:G3', 'Period Length (days):', format2)
        sheet.write('H3', period_length, format3)
        sheet.write('A4', "Partner's:", format2)
        sheet.merge_range('B4:C4', account_type_name, format3)
        sheet.merge_range('E4:F4', 'Target Moves:', format2)
        sheet.merge_range('G4:H4', target_move_name, format3)
        sheet.set_column(0, 0, 20)
        # # if sales_person_wise:
        # #     sheet.set_column(1, 1, 20)
        # #     sheet.merge_range(5, 0, 7, 8, "Aged Partner Balance", format1)
        # # else:
        sheet.merge_range(5, 0, 7, 7, "Aged Partner Balance", format1)
        row_value = 8
        column_value = 0
        # # if sales_person_wise:
        # #     sheet.write(row_value, column_value, "Sales Person", format2)
        # #     column_value += 1
        sheet.write(row_value, column_value, "Partners", format2)
        sheet.write(row_value, column_value + 1, "Not due", format2)
        sheet.write(row_value, column_value + 2, "0-" + str(period_length), format2)
        sheet.write(row_value, column_value + 3, str(period_length) + "-" + str(2 * period_length), format2)
        sheet.write(row_value, column_value + 4, str(2 * period_length) + "-" + str(3 * period_length), format2)
        sheet.write(row_value, column_value + 5, str(3 * period_length) + "-" + str(4 * period_length), format2)
        sheet.write(row_value, column_value + 6, "+" + str(4 * period_length), format2)
        sheet.write(row_value, column_value + 7, "Total", format2)
        row_value += 1
        column_value = 0
        if move_lines:
            sheet.write(row_value, column_value, "Account Total", format2)
            sheet.write(row_value, column_value + 1, total[6], format2)
            sheet.write(row_value, column_value + 2, total[4], format2)
            sheet.write(row_value, column_value + 3, total[3], format2)
            sheet.write(row_value, column_value + 4, total[2], format2)
            sheet.write(row_value, column_value + 5, total[1], format2)
            sheet.write(row_value, column_value + 6, total[0], format2)
            sheet.write(row_value, column_value + 7, total[5], format2)
            row_value += 1
            for i in move_lines:
                partner_ref = self.env['res.partner'].browse(i['partner_id']).ref
                if partner_ref:
                    partner_ref = "[" + str(partner_ref) + "] "
                    partner_name = partner_ref + str(i['name'])
                else:
                    partner_name = str(i['name'])
                sheet.write(row_value, column_value, partner_name, format3)
                sheet.write(row_value, column_value + 1, i['direction'], format3)
                sheet.write(row_value, column_value + 2, i['4'], format3)
                sheet.write(row_value, column_value + 3, i['3'], format3)
                sheet.write(row_value, column_value + 4, i['2'], format3)
                sheet.write(row_value, column_value + 5, i['1'], format3)
                sheet.write(row_value, column_value + 6, i['0'], format3)
                sheet.write(row_value, column_value + 7, i['total'], format3)
                row_value += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()