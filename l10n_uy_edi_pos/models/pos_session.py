# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        # if self.config_id.module_pos_hr:
        #     loaded_data['employee_by_id'] = {employee['id']: employee for employee in loaded_data['hr.employee']}

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        new_model = 'res.city'
        if new_model not in result:
            result.append(new_model)
        return result

    def _loader_params_res_city(self):
        return {'search_params': {'domain': [], 'fields': ['name', 'zipcode', 'country_id','state_id'], 'load': False}}

    def _get_pos_ui_res_city(self, params):
        return self.env['res.city'].search_read(**params['search_params'])

    def _loader_params_res_partner(self):
        res = super()._loader_params_res_partner()
        fields = res.get('search_params', {}).get('fields', [])
        fields+=['city_id', 'uy_doc_type']
        res['search_params']['fields'] = fields
        return res