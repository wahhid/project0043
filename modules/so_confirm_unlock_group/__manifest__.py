# -*- coding: utf-8 -*-
{
    'name': "SW - SO Privileged Confirm & Unlock",
    'summary': """
            Limited Access on SO Cnfirmation and Unocking.
                """,
    'description': """
         Decide and limit the access of confirming & unlocking sale orders.
                """,
    'author': "Smart Way Business Solutions",
    'website': "https://www.smartway.co",
    'category': 'Accounting',
    'version': '12.0.1.0',
    'depends': ['base', 'sale'],
    'data': [
        'security/groups.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
    'auto_install': False,
    'ilcense':  "Other proprietary",
    'images':  ["static/description/image.png"],


}