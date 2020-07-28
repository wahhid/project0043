{
    "name": "Account Enhancement",
    "summary": "Account Enhancement for Project 0043",
    "version": "12.0.1.0.0",
    "author": "Wahyu Hidayat, "
              "WAHE",
    "category": "Product",
    "website": "https://www.jakc-labs.com",
    "license": "AGPL-3",
    'data': [
        'views/account_invoice_report.xml',
        'views/account_invoice_template.xml',
        'views/res_company_view.xml',
        'views/account_invoice_view.xml',
    ],
    "depends": [
        "account",
        "abs_total_discount_invoice",
        "stock_picking_invoice_link",
    ],
    "external_dependencies": {"python" : ["num2words"]},
    "installable": True,
}
