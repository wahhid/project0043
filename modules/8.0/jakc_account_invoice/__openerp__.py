{
    'name': 'Jakc Labs - Enchance Account Invoice',
    'version': '8.0.0.1.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'summary': 'Enchance Account Invoice',
    'author': "Jakc Labs",
    'website': 'http://www.jakc-labs.com/',
    'depends': [
        'base','account', 'sale_discount_total',
    ],
    'data': [
        'jakc_account_invoice_view.xml',
    ],
    'installable': True,
    'application': True,
}
