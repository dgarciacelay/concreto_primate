# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class Currency(models.Model):
    _inherit = 'res.currency'
    
    uy_currency_code = fields.Selection(selection="_get_currency_code", string="Uruguayan Currency Code")
    
    @api.model
    def _get_currency_code(self):
        return self.env['uy.datas'].get_by_code("UY.CURRENCY.CODE")