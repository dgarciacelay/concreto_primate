# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

{
    'name': 'Partial Invoice Payment Reconciliation',
    'version': '15.0.0.0',
    'category': 'Accounting',
    "license": "OPL-1",
    'summary': 'partial invoice payment invoice partial reconciliation partial reconciliation partial payment reconciliation customer partial invoice payment reconciliation customer payment partial reconciliation multiple invoice partial reconciliation multiple partial reconcilation',
    'description': """
        partial invoice payment
        invoice partial reconciliation
        customer invoice partial reconciliation
        customer partial payment reconciliation
        partial reconciliation payment
        partial reconciliation invoice payment
        multiple invoice partial reconciliation
        multiple invoice reconciliation
        multiple invoice payment reconciliation
        single invoice reconciliation
        single payment reconciliation with multiple invoices
        partial payment
        customer payment partial reconciliation
        partial reconciliation from outstanding payment
        partial reconciliation from payment
        customer partial invoice payment from customer payment
        customer invoice reconciliation
        customer payment reconciliation
        invoice reconciliation form outstanding payment
        check outstanding balance
        check debit
        check credit
        check remaining outstanding balance
        customer pay partially from outstanding balance
        pay partially
        partially pay invoice amount
        partially pay multiple invoice
        
        
""",
    "price": 40,
    "currency": 'EUR',
    'author': 'Sitaram',
    'depends': ['account'],
    "data": [
        "data/partial_matching_number_data.xml",
        "security/ir.model.access.csv",
        "views/inherited_account_move_view.xml",
        "views/inherited_account_payment_view.xml",
        "wizard/partial_payment_view.xml",
        "wizard/partial_multi_payment_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/sr_partial_invoice_payment/static/src/js/inherited_account_payment_field.js",
        ],
        "web.assets_qweb": [
            "sr_partial_invoice_payment/static/src/xml/**/*",
        ],
    },
    'website':'https://sitaramsolutions.in',
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/jv9_flI09uY',
    "images":['static/description/banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
