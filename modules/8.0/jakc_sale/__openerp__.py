{
    'name': 'Jakc Labs - Sale Enhancement',
    'version': '8.0.0.1.0',
    'category': 'Sale',
    'license': 'AGPL-3',
    'summary': 'Sale Enhancement',
    'author': "Jakc Labs",
    'website': 'http://www.jakc-labs.com/',
    'depends': [
        'sale',
        'delivery',
        'stock',
    ],
    'data': [
        'jakc_sale_view.xml',
        'res_company_view.xml',
        'security/sale_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
