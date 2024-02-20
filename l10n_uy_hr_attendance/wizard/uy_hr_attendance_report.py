# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import pytz

class UyHrAttendanceReport(models.Model):
    _name = "uy.hr.attendance.report"
    _description = "Attendance Report"

    start_date = fields.Date("Start Date", required=True)
    end_date = fields.Date("End Date", required=True)

    def button_export_xlsx(self):
        self.ensure_one()
        if self.start_date>self.end_date:
            raise exceptions.ValidationError(_("The start date cannot be greater than the end date."))
        data = {}
        return self.env.ref('l10n_uy_hr_attendance.attendance_xlsx').report_action(self, data=data)

        return {}