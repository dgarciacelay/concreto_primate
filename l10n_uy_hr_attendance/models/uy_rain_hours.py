# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import datetime, timedelta
from operator import itemgetter

import pytz
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
from odoo.osv.expression import AND, OR
from odoo.tools.float_utils import float_is_zero


class UyRainHours(models.Model):
    _name = "uy.rain.hours"
    _description = "Uruguayan rain hours"
    _order = "check_in desc"

    department_id = fields.Many2one('hr.department', required=True)
    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=True)
    check_out = fields.Datetime(string="Check Out")
    uy_rain_hours = fields.Float(string='Rain Hours', compute='_compute_hours', readonly=True)

    @api.depends('check_in', 'check_out')
    def _compute_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                delt = attendance.check_out - attendance.check_in
                attendance.uy_rain_hours = delt.total_seconds() / 3600.0
            else:
                attendance.uy_rain_hours = False