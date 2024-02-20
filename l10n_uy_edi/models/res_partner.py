# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _

class Partner(models.Model):
    _inherit = 'res.partner'
    
    @api.model
    def _get_uy_doc_type(self):
        res = self.env['uy.datas'].get_selection("UY.DOC.TYPE")
        return res
    