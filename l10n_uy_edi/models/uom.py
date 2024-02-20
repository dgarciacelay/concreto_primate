# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class UoM(models.Model):
    _inherit = 'uom.uom'
    
    uy_unit_code = fields.Selection(selection="_get_uy_unit_code", string="Uruguayan Unit Code")

    @api.model
    def _get_uy_unit_code(self):
        return self.env['uy.datas'].get_by_code("UY.UNIT.CODE")
