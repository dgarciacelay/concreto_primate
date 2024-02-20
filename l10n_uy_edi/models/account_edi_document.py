# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
import re
from base64 import decodebytes

_logger = logging.getLogger(__name__)


class AccountEdiDocument(models.Model):
    _inherit = 'account.edi.document'
    
    uy_number = fields.Char("Number")
    uy_send_number = fields.Integer("Send Number", compute = '_compute_uy_send_number', store = True)
    uy_send_date = fields.Datetime("Send Date")
    
    uy_error_code = fields.Selection("_get_uy_error_code", string= "Error Code", readonly=True)
    
    uy_document_state = fields.Selection(selection=[('AE', 'Comprobante aceptado'), 
                                                 ('BE', 'Comprobante rechazado')], string="Document Status",
                                      readonly=True)
    uy_cfe_serie=fields.Char("Serie", readonly=True)
    uy_cfe_number=fields.Char("CFE Number", readonly=True)
    uy_qr_id = fields.Many2one('ir.attachment', "Qr Code")
    uy_security_code = fields.Char("Security Code", readonly=True)
    uy_constancy = fields.Char("Constancy", readonly=True)
    uy_constancy_serie = fields.Char("Constancy Serie", readonly=True)
    uy_constancy_from = fields.Char("Constancy From", readonly=True)
    uy_constancy_to = fields.Char("Constancy To", readonly=True)
    uy_constancy_vto = fields.Char("Constancy Vto", readonly=True)
    uy_url_code = fields.Char("Url Code", readonly=True)
    uy_cfe_id = fields.Char("CFE ID")
    uy_cfe_hash = fields.Char("CFE Hash")
    uy_invoice_url = fields.Char("Invoice Url")

    @api.model
    def _get_uy_error_code(self):
        return self.env['uy.datas'].get_by_code("UY.EFACTURA.ERROR")
    
    @api.depends('uy_number')
    def _compute_uy_send_number(self):
        for edi in self:
            if edi.uy_number:
                number = re.findall("^\w+\-*(\d+)", edi.uy_number)
                edi.uy_send_number = number and int(number[0]) or 0
            else:
                edi.uy_send_number = 0
            
    
    def create_uy_sequence(self, seq_id=False):
        self.ensure_one()
        company_id = self.move_id.company_id.id
        vals = {}
        vals['name'] = _("UY EDI Sequence")
        vals['code'] = 'uy.edi.number'
        vals['implementation'] = 'standard'
        vals['prefix'] = 'EDI-'
        vals['padding'] = 6
        vals['use_date_range'] = False
        vals['company_id'] = company_id
        if not seq_id:
            seq_id = self.env['ir.sequence'].create(vals)
        else:
            seq_id.write(vals)
        return seq_id
        
    def get_uy_number(self):
        self.ensure_one()
        company_id = self.move_id.company_id.id
        seq_id = self.env['ir.sequence'].search([('code', '=', 'uy.edi.number'), ('company_id', '=', company_id)], 
                                                 limit =1, order='company_id')
        if not seq_id:
            seq_id = self.create_uy_sequence()
        self.uy_number = seq_id.next_by_id()
