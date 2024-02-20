# -*- coding: utf-8 -*-
{
    'name': "Uruguayan docs validators",

    'summary': """
        Validate RUT and C.I.
        """,

    'description': """
    Validate RUT and C.I.
    """,

    'author': "Grupo YACCK",
    'website': "www.grupoyacck.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization/Base',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
    ],

    # always loaded
    'data': [
        'views/res_partner_view.xml',
    ],
}