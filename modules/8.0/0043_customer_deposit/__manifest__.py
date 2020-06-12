{
    "name": "Customer Deposit",
    "summary": "Customer Deposit for Project 0043",
    "version": "12.0.0.1.0",
    "author": "Wahyu Hidayat, "
              "WAHE",
    "category": "Accounting",
    "website": "https://www.jakc-labs.com",
    "license": "AGPL-3",
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/product_pricelist_view.xml',
        'views/customer_deposit_view.xml',
        'views/sale_order_view.xml',
        'views/account_journal_view.xml',
        'views/account_payment_view.xml',
        'views/account_invoice_view.xml',
        'data/ir_sequence_data.xml',
    ],
    "depends": [
        "product","account","sale"
    ],
    "installable": True,
}
