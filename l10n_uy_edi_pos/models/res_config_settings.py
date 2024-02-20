# -*- coding: utf-8 -*-

from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_uy_anonymous_id = fields.Many2one('res.partner', related='pos_config_id.uy_anonymous_id', readonly=False, string='Anonymous Partner')