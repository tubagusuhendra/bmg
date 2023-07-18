# -*- coding: utf-8 -*-
{
    'name': "Registration Form",
    'summary': """Registration""",
    'author': 'Tubagus Suhendra',
    'company': 'BMG',
    'maintainer': 'BMG',
    "category": "Registration",
    'website': "http://www.bmg.com",
    "version": "14.0.1.0.0",
    'depends': ['base','mail','portal'],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/bmg_registration_view.xml',
    ],
    'license': 'AGPL-3',
    "installable": True,
}
