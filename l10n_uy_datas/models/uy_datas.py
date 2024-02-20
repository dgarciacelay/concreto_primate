# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class UyDgiTables(models.Model):
    _name = 'uy.datas'
    _description = 'Uruguayan Datas'

    name = fields.Char("Name", required=True)
    company_id = fields.Many2one("res.company", "Company")
    code = fields.Char("Code", required=True)
    data_code = fields.Char("Table Code", required=True)
    active= fields.Boolean("Active", default=True)
    description = fields.Text("Description")
    
    _sql_constraints = [
        ('table_code_uniq', 'unique(code, data_code)', 'The code of the table must be unique by table code !')
    ]
    
    @api.model
    def get_by_code(self, data_code):
        res=[]
        dgi_codes=self.search([('data_code', '=', data_code)])
        if dgi_codes:
            res = [(str(dgi_code.code),str(dgi_code.name)) for dgi_code in dgi_codes]
        return res
        