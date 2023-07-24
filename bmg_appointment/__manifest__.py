# -*- coding: utf-8 -*-
{
    'name': "Appointment",
    'summary': """Appointment""",
    'author': 'Tubagus Suhendra',
    'company': 'BMG',
    'maintainer': 'BMG',
    "category": "Appointment",
    'website': "http://www.bmg.com",
    "version": "14.0.1.0.0",
    'depends': ['base','mail','portal', 'hr'],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/bmg_appointment_view.xml',
    ],
    'license': 'AGPL-3',
    "installable": True,
}
