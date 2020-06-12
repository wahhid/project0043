{
    'name': 'Jakc Labs - Stock Enhancement',
    'version': '8.0.0.1.0',
    'category': 'Stock',
    'license': 'AGPL-3',
    'summary': 'Stock  Enhancement',
    'author': "Jakc Labs",
    'website': 'http://www.jakc-labs.com/',
    'depends': [
        'stock',
        'stock_sale_order_line',
    ],
    'data': [
        'report/report_stock_inventory.xml',
        'report/report_stock_inventory_template.xml',
        'wizard/stock_transfer_details_view.xml',
        'wizard/stock_inventory_view.xml',
        'stock_view.xml',
        'views/product_view.xml',
    ],
    'installable': True,
    'application': True,
}
