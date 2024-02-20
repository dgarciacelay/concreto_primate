# -*- coding: utf-8 -*-
{
    'name': "l10n_uy_hr_attendance",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_attendance', 'report_xlsx'],

    # always loaded
    'data': [
        'data/hr_attendance_data.xml',
        'security/ir.model.access.csv',
        'views/hr_attendance_view.xml',
        'views/uy_rain_hours_view.xml',
        'wizard/uy_hr_attendance_report_view.xml',
        'report/report_uy_attendance.xml'
    ],

}
