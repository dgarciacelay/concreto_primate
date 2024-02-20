# -*- coding: utf-8 -*-
{
    'name': "Uruguayan Sale EDI",

    'summary': """
        Sale, Uruguayan EDI""",

    'description': """
        Uruguayan Sale EDI
    """,

    'author': "Grupo YACCK",
    'website': "http://www.grupoyacck.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'sale',
        'l10n_uy_edi',
        ],

    # always loaded
    'data': [
    ]
}
