# -*- coding: utf-8 -*-
{
    'name': "Uruguayan toponyms",

    'summary': """Uruguayan toponyms""",

    'description': """
        Uruguayan toponyms
	    List Uruguayan toponyms
    """,

    'author': "GrupoYACCK",
    'website': "http://www.grupoyacck.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization/Toponyms',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base_address_extended'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'data/uy_country_data.xml',
        'data/res_country_data.xml',
    ],
    # only loaded in demonstration mode
    #'demo': [
    #    'demo/demo.xml',
    #],
}
