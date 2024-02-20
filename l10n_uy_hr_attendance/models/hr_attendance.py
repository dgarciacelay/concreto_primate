# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import datetime, timedelta
from operator import itemgetter

import pytz
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
from odoo.osv.expression import AND, OR
from odoo.tools.float_utils import float_is_zero


class HrAttendance(models.Model):
    _inherit = "hr.attendance"



    uy_note = fields.Char("Note")
    uy_normal_hours = fields.Float("Normal Hrs", compute='_compute_uy_hours', readonly=True)
    uy_extra_hours = fields.Float("Extra Hrs", compute='_compute_uy_hours', readonly=True)
    uy_rain_hours = fields.Float("Rain Hrs", compute="_compute_uy_rain_hours")
    uy_break = fields.Boolean("Break")
    department_id = fields.Many2one('hr.department', related="employee_id.department_id",
                                    depends=["employee_id"], store=True)

    # def _get_uy_worked_hours(self, employee, check_in, check_out, break_hours = False):
    #     res = []
    #     employee_id = self.env['hr.employee'].browse(employee)
    #     tz = pytz.timezone(employee_id.resource_calendar_id.tz and self.env.context.get('tz') or
    #                        self.env.user.tz or 'UTC')
    #     server_tz = pytz.timezone('UTC')
    #     local_check_in = server_tz.localize(check_in).astimezone(tz)
    #     local_check_out = server_tz.localize(check_out).astimezone(tz)
    #     total_days = (local_check_out - local_check_in).days
    #     break_hours = 0.0
    #     extra_hours = 0.0
    #     total_hours = 0.0
    #     for day in range(total_days):
    #         temp_check_in = tz.localize(fields.Datetime.from_string(
    #             (local_check_in + timedelta(days=day)).strftime("%Y-%m-%d"))
    #         )
    #         local_day = temp_check_in.strftime('%w')
    #         odoo_day = int(local_day) - 1 == -1 and '6' or str(int(local_day) - 1)
    #         calendar_ids = employee_id.resource_calendar_id.attendance_ids.filtered(lambda s: s.dayofweek == odoo_day)
    #         for calendar_id in calendar_ids:
    #             #Hora Extra al inicio de jornada
    #             if (local_check_in+timedelta(days=day)) <= (local_day + timedelta(hours=calendar_id.hour_from)):
    #                 extra_hours +=



    @api.depends('department_id', 'check_in', 'check_out', 'uy_break')
    def _compute_uy_rain_hours(self):
        for attendance in self:
            # rain_id = self.env['uy.rain.hours'].search([('department_id', '=', attendance.department_id.id),
            #                                             ('check_in','>=',attendance.check_in),('check_in','<=',attendance.check_out),
            #                                             '|',('check_out','>=',attendance.check_in),('check_out','<=',attendance.check_out)], limit=1)

            if attendance.check_in and attendance.check_out:
                query = """SELECT id FROM uy_rain_hours  WHERE department_id=%s
                        AND (check_in BETWEEN %s AND %s OR check_out BETWEEN %s AND %s)
                        OR (check_in<%s AND check_out>%s);"""
                self.env.cr.execute(query, [attendance.department_id.id, attendance.check_in,
                                            attendance.check_out, attendance.check_in,
                                            attendance.check_out,attendance.check_in,
                                            attendance.check_out])
                rain_vals = self.env.cr.fetchall()
                rains = []
                for rain_val in rain_vals:
                    rains.append(rain_val[0])
                rain_ids = rain_vals and self.env['uy.rain.hours'].browse(rains) or False
                delta = 0.0
                if rain_ids:
                    for rain_id in rain_ids:
                        if rain_id.check_in <= attendance.check_in <= rain_id.check_out \
                                and rain_id.check_in <= attendance.check_out <= rain_id.check_out:
                            temp_delta = attendance.check_out - attendance.check_in
                        elif rain_id.check_in>=attendance.check_in and rain_id.check_out<=attendance.check_out:
                            temp_delta = rain_id.check_out - rain_id.check_in
                        elif rain_id.check_in>=attendance.check_in:
                            temp_delta = attendance.check_out - rain_id.check_in
                        else:
                            temp_delta = rain_id.check_out - attendance.check_in
                        delta += (temp_delta.total_seconds()) / 3600.0
                attendance.uy_rain_hours = delta
            else:
                attendance.uy_rain_hours = False

    def _get_uy_in_out_hours(self):
        self.ensure_one()
        tz = pytz.timezone(self.employee_id.resource_calendar_id.tz or self.env.context.get('tz') or self.env.user.tz or 'UTC')
        server_tz = pytz.timezone('UTC')
        day = tz.localize(self.check_in).strftime('%w')
        local_day = tz.localize(fields.Datetime.from_string(tz.localize(self.check_in).strftime("%Y-%m-%d")))
        odoo_day = int(day) - 1 == -1 and '6' or str(int(day) - 1)
        attendance_ids = self.employee_id.resource_calendar_id.attendance_ids.filtered(lambda s: s.dayofweek==odoo_day)

        morning_hour_from = attendance_ids and attendance_ids.filtered(lambda s: s.day_period == 'morning')[0].hour_from or False
        morning_hour_to = attendance_ids and attendance_ids.filtered(lambda s: s.day_period == 'morning')[0].hour_to or False
        afternoon_hour_from = attendance_ids and attendance_ids.filtered(lambda s: s.day_period == 'afternoon')[0].hour_from or False
        afternoon_hour_to = attendance_ids and attendance_ids.filtered(lambda s: s.day_period == 'afternoon')[0].hour_to or False

        morning_in_hours = (local_day + timedelta(hours=morning_hour_from)).astimezone(pytz.timezone('UTC'))
        morning_out_hours = (local_day + timedelta(hours=morning_hour_to)).astimezone(pytz.timezone('UTC'))
        afternoon_in_hours = (local_day + timedelta(hours=afternoon_hour_from)).astimezone(pytz.timezone('UTC'))
        afternoon_out_hours = (local_day + timedelta(hours=afternoon_hour_to)).astimezone(pytz.timezone('UTC'))

        break_hours = (afternoon_in_hours - morning_out_hours).total_seconds()/3600.0
        extra_hours = 0.0
        if server_tz.localize(self.check_in) < morning_in_hours:
            extra_hours+=(morning_in_hours - server_tz.localize(self.check_in)).total_seconds()/3600.0
        if server_tz.localize(self.check_out) > afternoon_out_hours:
            extra_hours += (server_tz.localize(self.check_out) - afternoon_out_hours).total_seconds() / 3600.0
        self.uy_extra_hours = extra_hours

    @api.depends('check_in', 'check_out', 'uy_break')
    def _compute_uy_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                break_hours = 0
                if not attendance.uy_break:
                    break_hours = 3600.0
                delta = attendance.check_out - attendance.check_in
                attendance._get_uy_in_out_hours()
                attendance.uy_normal_hours = (delta.total_seconds() - break_hours) / 3600.0
            else:
                attendance.uy_normal_hours = False
                attendance.uy_extra_hours = False
