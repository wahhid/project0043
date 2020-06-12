{
    "name": "Sale Order Enhancement",
    "summary": "Sale Order Enhancement for Project 0043",
    "version": "12.0.1.0.0",
    "author": "Wahyu Hidayat, "
              "WAHE",
    "category": "Sales",
    "website": "https://www.jakc-labs.com",
    "license": "AGPL-3",
    'data': [
        'views/sale_order_view.xml',
        'wizards/wizard_sale_recap_report_view.xml',
        'wizards/wizard_sale_retur_recap_report_view.xml',
        'wizards/wizard_sale_item_report_view.xml',
        'wizards/wizard_sale_item_cust_report_view.xml',
        'wizards/wizard_sale_item_cust_area_report_view.xml',
        'reports/sale_recap_report_view.xml',
        'reports/sale_retur_recap_report_view.xml',
        'reports/sale_item_report_view.xml',
        'reports/sale_item_cust_report_view.xml',
        'reports/sale_item_cust_area_report_view.xml',
    ],
    "depends": [
        "sale","sales_team","sale_stock","sale_order_lot_selection",
    ],
    "installable": True,
}
