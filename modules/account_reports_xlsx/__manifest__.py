# -*- coding: utf-8 -*-
{
    'name': 'Accounting Report Excel',
    'version': '12.0.1.1.3',
    'author': 'Cybrosys Techno Solutions',
    'website':  "http://www.cybrosys.com/",
    'category': 'Accounting',
    'live_test_url': 'https://www.youtube.com/watch?v=Sch1VcrunT0&list=PLeJtXzTubzj_wOC0fzgSAyGln4TJWKV4k&index=33',
    'summary': """Generates Excel report for Partner Ledger,General Ledger,Balance Sheet,
                Profit and Loss,Aged Partner Balance.""",
    'description': """Generates Excel reports 
                    accounts reports account reports accounting excel reports account excel reports""",
    'depends': ['base','account'],
    'data': [
        'views/action_manager.xml',
        'views/account_financial_report_data.xml',
        'security/ir.model.access.csv',
        'wizard/partner_ledger_wizard_view.xml',
        'wizard/account_report_aged_partner_balance_view.xml',
        'wizard/account_report_general_ledger_view.xml',
        'wizard/account_financial_report_view.xml',
     ],
    'images': [],
    'demo': [],
    'license': 'OPL-1',
    'price': 19.99,
    'currency': 'EUR',
    'images': ['static/description/banner.jpg'],
    'auto_install': False,
    'installable': True,
    'application': True,
}