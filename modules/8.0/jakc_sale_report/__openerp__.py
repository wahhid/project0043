# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale - Enchance Report',
    'version': '1.0.1',
    'category': 'Sale',
    'author': 'Jakc Labs',
    'sequence': 20,
    'summary': 'Sale - Enchance Report',
    'description': """
Sale - Enchance Report
===============================
Sale - Enchance Report
    """,
    'depends': ['sale'],
    'data': [
        'sale_order_report.xml',
        'wizard/sale_report.xml',
        'views/report_sale_order.xml',

    ],
    'installable': True,
    'application': True,
    'website': 'https://www.jakc-labs.com',
    'auto_install': False,
}
