# -*- coding: utf-8 -*-
{
    'name': "UY EDI POS Epson",

    'summary': """
        EDI POS Epson""",

    'description': """
        Print on Epson POS Printer EDI pdf invoices 
    """,

    'author': "Grupo YACCK",
    'website': "https://www.grupoyacck.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['l10n_uy_edi_pos', 'pos_epson_printer'],

    # always loaded
    'data': [
    ],
    'assets': {
            'point_of_sale.assets': [
                'l10n_uy_edi_pos_epson/static/src/js/printers.js',
                'l10n_uy_edi_pos_epson/static/src/js/Screens/ReceiptScreen.js',
            ],
    },
}
