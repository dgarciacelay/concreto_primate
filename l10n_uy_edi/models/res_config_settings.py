# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from pyCFE import Servidor

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    def action_cfe_config_wizard(self):
        self.ensure_one()
        context = dict(self.env.context)
        context['active_id'] = self.id
        return {
            'name': _('CFE Wizard'),
            'res_model': 'uy.cfe.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('l10n_uy_edi.view_form_uy_cfe_wizard').id,
            'context': context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
