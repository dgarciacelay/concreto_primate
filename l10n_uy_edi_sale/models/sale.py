# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        return res
    
    def _create_invoices(self, grouped=False, final=False, date=None):
        move_ids = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, date=date)
        for move_id in move_ids:
            default_journal_id = move_id.journal_id.id
            if move_id.move_type == 'out_invoice':
                if move_id.partner_id.uy_doc_type == '2':
                    move_id.uy_document_code = '111'
                    journal_id = self.env['account.journal'].search([('type','=','sale'),('uy_document_code','=','111'),
                                                                     ('company_id','=',self.company_id.id)], limit=1)
                    move_id.journal_id = journal_id.id or default_journal_id
                else:
                    move_id.uy_document_code = '101'
                    journal_id = self.env['account.journal'].search([('type','=','sale'),('uy_document_code','=','101'),
                                                                     ('company_id','=',self.company_id.id)], limit=1)
                    move_id.journal_id = journal_id.id or default_journal_id
            elif move_id.move_type == 'out_refund':
                invoice_ids = move_id.invoice_line_ids.mapped('sale_line_ids').mapped('order_id').mapped('invoice_ids').mapped('edi_document_ids').filtered(lambda s: s.state == 'sent').mapped('move_id')
                if invoice_ids:
                    product_ids = move_id.invoice_line_ids.mapped('product_id').ids
                    invoice_line_ids = invoice_ids.filtered(lambda s: s.id != move_id.id and s.state == 'posted').invoice_line_ids.filtered(lambda l: l.product_id.id in product_ids)
                    invoice_id = invoice_line_ids and invoice_line_ids[0].move_id.id or False
                    move_id.reversed_entry_id = invoice_id
                if move_id.partner_id.uy_doc_type == '2':
                    move_id.uy_document_code = '112'
                    journal_id = self.env['account.journal'].search([('type','=','sale'),('uy_document_code','=','112'),
                                                                     ('company_id','=',self.company_id.id)], limit=1)
                    if not journal_id:
                        journal_id = self.env['account.journal'].search([('type','=','sale'),('uy_document_code','=','111'),
                                                                         ('company_id','=',self.company_id.id),('refund_sequence','=',True)], limit=1)
                    move_id.journal_id = journal_id.id or default_journal_id
                else:
                    move_id.uy_document_code = '102'
                    journal_id = self.env['account.journal'].search([('type','=','sale'),('uy_document_code','=','102'),
                                                                     ('company_id','=',self.company_id.id)], limit=1)
                    if not journal_id:
                        journal_id = self.env['account.journal'].search([('type','=','sale'),('uy_document_code','=','101'),
                                                                         ('company_id','=',self.company_id.id),('refund_sequence','=',True)], limit=1)
                    move_id.journal_id = journal_id.id or default_journal_id
        return move_ids
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    def _prepare_invoice_line(self, **optional_values):
        if self.tax_id.filtered(lambda s:s.uy_tax_type == '0'):
            optional_values['uy_invoice_indicator'] = '1'
        if self.tax_id.filtered(lambda s:s.uy_tax_type == '10'):
            optional_values['uy_invoice_indicator'] = '2'
        if self.tax_id.filtered(lambda s:s.uy_tax_type == '22'):
            optional_values['uy_invoice_indicator'] = '3'
        return super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)