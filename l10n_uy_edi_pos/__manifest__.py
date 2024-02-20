# -*- coding: utf-8 -*-
{
    'name': "Uruguayan EDI POS",

    'summary': """
        POS, Uruguayan EDI""",

    'description': """
        POS, Uruguayan EDI
    """,

    'author': "Grupo YACCK",
    'website': "http://www.grupoyacck.com",
    'category': 'Sales/Point of Sale',
    'version': '0.1',
    'depends': [
        'account',
        'l10n_uy_edi',
        'point_of_sale'
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
            'point_of_sale.assets': [
            'l10n_uy_edi_pos/static/src/js/models.js',
            'l10n_uy_edi_pos/static/src/js/Screens/PaymentScreen.js',
            'l10n_uy_edi_pos/static/src/js/Screens/ReceiptScreen.js',
            'l10n_uy_edi_pos/static/src/js/Screens/PartnerListScreen/PartnerDetailsEdit.js',
            'l10n_uy_edi_pos/static/src/xml/Screens/PartnerListScreen/PartnerDetailsEdit.xml'
        ],
    },
}
