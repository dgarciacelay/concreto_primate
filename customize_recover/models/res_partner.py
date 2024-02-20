
from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    fantasy_name = fields.Char()
    total_due = fields.Float()