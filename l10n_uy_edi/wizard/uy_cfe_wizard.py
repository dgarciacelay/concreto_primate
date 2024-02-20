# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from pyCFE import Servidor


class UyCfeWizard(models.TransientModel):
    _name = "uy.cfe.wizard"
    _description = "CFE Wizard"

    uy_username = fields.Char("Username", related="company_id.uy_username", readonly=False)
    uy_password = fields.Char("Password/Token", related="company_id.uy_password", readonly=False)
    uy_server_url = fields.Char("Server URL", related="company_id.uy_server_url", readonly=False)
    uy_server = fields.Selection(selection='get_uy_server', string='Server',
                                 readonly=False)
    uy_efactura_print_mode = fields.Selection(selection='get_uy_efactura_print_mode', string='Print mode',
                                              readonly=False)
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True,
                                 readonly=True)
    uy_branch_code = fields.Char("Branch Code")
    uy_resolution = fields.Char("Resolution")
    uy_verification_url = fields.Char("Verification Url")
    uy_company_id = fields.Char("Company Id")

    @api.model
    def get_uy_efactura_print_mode(self):
        return self.env['uy.datas'].get_by_code("UY.EFACTURA.PRINT.MODE")

    @api.model
    def get_uy_server(self):
        return Servidor().getServidores()

    @api.model
    def default_get(self, fields_list):
        values = super(UyCfeWizard, self).default_get(fields_list)
        if self.env.context['active_model'] == 'res.config.settings' and 'active_id' in self.env.context:
            active_settings_ids = self.env['res.config.settings'].browse(self.env.context['active_id'])
            company_id = active_settings_ids and active_settings_ids[0].company_id or False
            values['uy_username'] = company_id and company_id.uy_username or False
            values['uy_password'] = company_id and company_id.uy_password or False
            values['uy_server_url'] = company_id and company_id.uy_server_url or False
            values['uy_server'] = company_id and company_id.uy_server or False
            values['uy_efactura_print_mode'] = company_id and company_id.uy_efactura_print_mode or False
            values['uy_branch_code'] = company_id and company_id.uy_branch_code or False
            values['uy_resolution'] = company_id and company_id.uy_resolution or False
            values['uy_verification_url'] = company_id and company_id.uy_verification_url or False
            values['company_id'] = company_id and company_id.id or False
            values['uy_company_id'] = company_id and company_id.uy_company_id or False
        return values
    
    
    def appy_configuration(self):
        self.ensure_one()
        values = {}
        values['uy_username'] = self.uy_username or False
        values['uy_password'] = self.uy_password or False
        values['uy_server_url'] = self.uy_server_url or False
        values['uy_server'] = self.uy_server or False
        values['uy_efactura_print_mode'] = self.uy_efactura_print_mode or False
        values['uy_branch_code'] = self.uy_branch_code or False
        values['uy_resolution'] = self.uy_resolution or False
        values['uy_verification_url'] = self.uy_verification_url or False
        values['uy_company_id'] = self.uy_company_id or False
        self.company_id.write(values)
    