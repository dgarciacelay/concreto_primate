# -*- coding: utf-8 -*-

from odoo import models, fields, api
from pyCFE import Servidor

class AccountJournal(models.Model):
    _inherit = "account.journal"

    uy_credit_note_id = fields.Many2one(comodel_name="account.journal", string="Credit Note", domain="[('type','=', 'sale')]")
    uy_dedit_note_id = fields.Many2one(comodel_name="account.journal", string="Debit Note", domain="[('type','=', 'sale')]")
    uy_document_code = fields.Selection(selection="_get_uy_invoice_code", string="Invoice Type Code")
    uy_server = fields.Selection(selection='get_uy_server', string='Server', related="company_id.uy_server")
    uy_efactura_print_mode = fields.Selection(selection='get_uy_efactura_print_mode', string='Print Mode')
    uy_is_edi_document = fields.Boolean("Is EDI Document", compute="_compute_uy_is_edi_document", store=True)

    @api.depends("edi_format_ids")
    def _compute_uy_is_edi_document(self):
        for journal_id in self:
            journal_id.uy_is_edi_document = bool(journal_id.edi_format_ids.filtered(lambda s: s.code == 'edi_uy_cfe'))

    @api.model
    def get_uy_server(self):
        return Servidor().getServidores()
    
    @api.model
    def get_uy_efactura_print_mode(self):
        return self.env['uy.datas'].get_by_code("UY.EFACTURA.PRINT.MODE")
    
    @api.model
    def _get_uy_invoice_code(self):
        return self.env['uy.datas'].get_by_code("UY.DOCUMENT.CODE")

class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'
    
    uy_payment_method = fields.Selection('_get_uy_payment_method', "Payment Method")
    
    @api.model
    def _get_uy_payment_method(self):
        return self.env['uy.datas'].get_by_code("UY.PAYMENT.METHOD")

class AccountTax(models.Model):
    _inherit = 'account.tax'
    
    uy_tax_type = fields.Selection(selection="_get_uy_tax_code", string="Tax Type")
    
    @api.model
    def _get_uy_tax_code(self):
        return self.env['uy.datas'].get_by_code("UY.TAX.TYPE")
    