# -*- coding: utf-8 -*-
{
    'name': "LWW Accounting",

    'summary': "",

    'description': """
Customization in LWW Accounting Module
    """,

    'author': "PT. Lintang Utama Infotek",
    'website': "https://www.lui.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    'application': False,
    'installable': True
}

