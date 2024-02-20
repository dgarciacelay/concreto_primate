# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    uy_anonymous_id = fields.Many2one('res.partner', string='Anonymous Partner')
