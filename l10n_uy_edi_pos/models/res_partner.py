# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create_from_ui(self, partner):
        if partner.get('city_id'):
            city_id = self.sudo().env['res.city'].search([('id','=',partner.get('city_id'))])
            # if not partner.get('state_id')  and not partner.get('id'):
            #     partner['state_id'] = city_id.state_id.id
            partner['city'] = city_id.name
            partner['zip'] = city_id.zipcode
        if not partner.get('country_id') and partner.get('state_id') and not partner.get('id'):
            state_id = self.env['res.country.state'].browse(partner.get('state_id'))
            partner['country_id'] = state_id.country_id.id
        res = super(ResPartner, self).create_from_ui(partner)
        return res