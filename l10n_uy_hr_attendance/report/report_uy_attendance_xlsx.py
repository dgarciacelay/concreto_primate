# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, _
from odoo.tools.misc import format_datetime
import pytz

class AttendanceXlsx(models.AbstractModel):
    _name = "report.l10n_uy_hr_attendance.attendance_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Attendance XLSX Report"

    def generate_xlsx_report(self, workbook, data, objs):
        sheet = workbook.add_worksheet("Report")
        row = 0
        col = 0
        sheet.write(row, col, _("Employee"))
        sheet.write(row, col + 1, _("Department"))
        sheet.write(row, col + 2, _("Check In"))
        sheet.write(row, col + 3, _("Check Out"))
        sheet.write(row, col + 4, _("Note"))
        sheet.write(row, col + 5, _("Work Hours"))
        sheet.write(row, col + 6, _("Normal Hours"))
        sheet.write(row, col + 7, _("Extra Hours"))
        sheet.write(row, col + 8, _("Rain Hours"))
        digit2 = workbook.add_format({'num_format': '0.00'})

        row += 1
        report_id = self.env['uy.hr.attendance.report'].browse(objs.ids)

        tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        server_tz = pytz.timezone('UTC')
        start_date = tz.localize(fields.Datetime.from_string(
            fields.Date.to_string(report_id.start_date)+" 00:00:00")
        ).astimezone(
            server_tz)
        end_date = tz.localize(fields.Datetime.from_string(
            fields.Date.to_string(report_id.end_date)+" 23:59:59")
        ).astimezone(server_tz)

        attendance_ids = self.env['hr.attendance'].search([('check_in','>=',start_date),('check_out','<=',end_date)])

        for attendance_id in attendance_ids:
            sheet.write(row, col, attendance_id.employee_id.name)
            sheet.write(row, col + 1, attendance_id.department_id.name)
            sheet.write(row, col + 2, format_datetime(self.env, attendance_id.check_in, dt_format='short'))
            sheet.write(row, col + 3, format_datetime(self.env, attendance_id.check_out, dt_format='short'))
            sheet.write(row, col + 4, attendance_id.uy_note or '')
            sheet.write(row, col + 5, attendance_id.worked_hours, digit2)
            sheet.write(row, col + 6, attendance_id.uy_normal_hours, digit2)
            sheet.write(row, col + 7, attendance_id.uy_extra_hours, digit2)
            sheet.write(row, col + 8, attendance_id.uy_rain_hours, digit2)
            row += 1