# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from pyCFE import Servidor

class Company(models.Model):
    _inherit = "res.company"

    uy_username = fields.Char("Username")
    uy_password = fields.Char("Password")
    uy_server_url = fields.Char("Server URL")
    uy_server = fields.Selection(selection='get_uy_server', string='Server')
    uy_efactura_print_mode = fields.Selection(selection='get_uy_efactura_print_mode', string='Print Mode')
    uy_branch_code = fields.Char("Branch Code")
    uy_sync_mode = fields.Boolean("Sync Mode", default = True)
    uy_resolution = fields.Char("Resolution")
    uy_verification_url  = fields.Char("Verification Url")
    uy_amount = fields.Float(string="Amount", digits=(16, 2), default=36300.00)
    uy_company_id = fields.Char("Company Id")

    @api.model
    def get_uy_efactura_print_mode(self):
        return self.env['uy.datas'].get_by_code("UY.EFACTURA.PRINT.MODE")
    
    @api.model
    def get_uy_server(self):
        return Servidor().getServidores()
    