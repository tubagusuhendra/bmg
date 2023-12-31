# -*- coding: utf-8 -*-
{
    'name': "Custom",
    'summary': """Custom""",
    'author': 'Tubagus Suhendra',
    'company': 'woosh',
    'maintainer': 'woosh',
    "category": "Custom",
    'website': "http://www.wooshfood.com",
    "version": "13.0.1.0.0",
    'depends': ['base',
                'mail',
                'portal', 
                'stock',
                'om_account_accountant',
                'om_account_asset',
                'om_account_budget',
],
    'data': [
        'data/sequence.xml',
        'security/group_users.xml',
        'views/stock_inventory_view.xml',
    ],
    'license': 'AGPL-3',
    "installable": True,
}
