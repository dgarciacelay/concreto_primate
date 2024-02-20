# -*- coding: utf-8 -*-
{
    'name': "Uruguayan Datas",

    'summary': """
        Uruguayan datas
        """,

    'description': """
        Uruguayan Datas
    """,

    'author': "Grupo YACCK",
    'website': "http://www.grupoyacck.com",

    'category': 'Localization/Custom',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'l10n_uy_vat',
        #'l10n_uy_toponyms',
    ],

    # always loaded
    'data': [
        'security/uy_datas_security.xml',
        'security/ir.model.access.csv',
        'views/uy_datas_view.xml',
    ],
}
