# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _
from pyCFE import Sobre, Documento
import re

class UySendCFE(models.AbstractModel):
    _name = 'uy.edi.send.cfe'
    _description = "No description"
    
    def get_server(self, invoice_id):
        vals = {}
        vals['url'] = invoice_id.company_id.uy_server_url
        vals['usuario'] = invoice_id.company_id.uy_username
        vals['clave'] = invoice_id.company_id.uy_password
        vals['codigo'] = invoice_id.company_id.uy_server
        if invoice_id.company_id.uy_server in ['biller']:
            vals['token'] = invoice_id.company_id.uy_password
        return vals
    
    def get_sobre(self, batch_id):
        vals = {}
        #if not batch_id.uy_number:
        batch_id.get_uy_number()
        if not batch_id.uy_send_date:
            to = self.with_context(tz='America/Montevideo')
            batch_id.uy_send_date = fields.Datetime.to_string(fields.Datetime.context_timestamp(to, 
                                                                      fields.Datetime.now()))
        vals['rutEmisor'] = batch_id.move_id.company_id.vat
        vals['numero']=str(batch_id.uy_send_number)
        vals['fecha'] = batch_id.uy_send_date.strftime("%Y-%m-%dT%H:%M:%S")
        vals['adenda'] = batch_id.move_id.narration and \
                         str(batch_id.move_id.narration).replace('<br>', '\n').replace('<br />', '\n').\
                             replace('<p>','').replace('</p>','\n') or  ""
        vals['impresion'] = batch_id.move_id.journal_id.uy_efactura_print_mode or \
                            batch_id.move_id.company_id.uy_efactura_print_mode or '1'
        return vals
    
       
    def _get_voucher(self, invoice_id):
        vals = {}
        vals['tipoCFE'] = invoice_id.uy_document_code
        vals['fecEmision'] = invoice_id.invoice_date.strftime("%Y-%m-%d")
        if invoice_id.invoice_date and invoice_id.invoice_date_due and invoice_id.invoice_date < invoice_id.invoice_date_due:
            vals['fecVencimiento'] = invoice_id.invoice_date_due.strftime("%Y-%m-%d")
            vals['formaPago'] = '2'
        else:
            vals['formaPago'] = '1'
        currency_name = invoice_id.currency_id.uy_currency_code or invoice_id.currency_id.name
        vals['moneda'] = currency_name

        vals['clauVenta'] = invoice_id.uy_clause
        vals['viaTransp'] = invoice_id.uy_transport
        vals['modVenta'] = invoice_id.uy_sales_mode
        return vals
    
    def _get_branch(self, partner_id, code=''):
        vals = {}
        vals['codigo'] = code
        vals['direccion'] = partner_id.street
        vals['ciudad'] = partner_id.city_id.name
        vals['departamento'] = partner_id.city_id.name
        vals['codPais'] = partner_id.country_id.code or "UY"
        return [vals]
    
    def _get_company(self, invoice_id):
        company_id= invoice_id.company_id
        vals = {}
        vals['numDocumento'] = company_id.vat
        vals['nombre'] = company_id.name
        vals['id'] = company_id.uy_company_id
        partner_id = company_id.partner_id
        if company_id.uy_branch_code:
            vals['sucursal'] = self._get_branch(partner_id, company_id.uy_branch_code)
        else:
            vals['direccion'] = partner_id.street
            vals['ciudad'] = partner_id.city_id.name
            vals['departamento'] = partner_id.state_id.name
            vals['codPais'] = partner_id.country_id.code
        return vals
        
    
    def _get_partner(self, invoice_id):
        partner_id = invoice_id.partner_id
        vals = {}
        vals['tipoDocumento'] = partner_id.uy_doc_type
        vals['numDocumento'] = partner_id.vat
        vals['direccion'] = partner_id.street
        vals['ciudad'] = partner_id.city_id.name
        vals['departamento'] = partner_id.state_id.name
        vals['codPais'] = partner_id.country_id.code or "UY"
        vals['nomPais'] = partner_id.country_id.name
        vals['nombre'] = partner_id.name
        vals['nombreFantasia'] = partner_id.uy_tradename or partner_id.name
        return vals
        
    def _get_total(self, invoice_id):
        vals = {}
        vals['tasaCambio'] = invoice_id.uy_currency_rate
        vals['mntNoGrv'] = invoice_id.uy_amount_unafected
        vals['mntNetoIVATasaMin'] = invoice_id.uy_tax_min_base
        vals['mntNetoIVATasaBasica'] = invoice_id.uy_tax_basic_base
        vals['ivaTasaMin'] = invoice_id.uy_tax_min_rate
        vals['ivaTasaBasica'] = invoice_id.uy_tax_basic_rate
        vals['mntIVATasaMin'] = invoice_id.uy_tax_min
        vals['mntIVATasaBasica'] = invoice_id.uy_tax_basic
        vals['mntTotal'] = invoice_id.amount_total
        vals['montoNF'] = invoice_id.uy_amount_untaxed # Revisar este campo en exportacion
        vals['mntPagar'] = invoice_id.amount_total
        return vals
        
    def _get_lines(self, invoice_line_ids):
        lines = []
        for line in invoice_line_ids:
            vals = {}
            vals['indicadorFacturacion'] = line.uy_invoice_indicator
            vals['descripcion'] = line.name[:80]
            vals['cantidad'] = line.quantity
            vals['unidadMedida'] = line.product_uom_id and line.product_uom_id.uy_unit_code or 'N/A'
            vals['precioUnitario'] = line.price_unit #line._get_price_total_and_subtotal(quantity=1)['price_total']
            vals['descuento'] = line.discount
            vals['codigo'] = line.product_id.default_code
            if line.discount>0.0:
                vals['descuentoMonto'] = line.uy_amount_discount
            if line.move_id.uy_gross_amount == '1':
                vals['montoItem'] =  line.price_total
            else:
                vals['montoItem'] =  line.price_subtotal
            #vals['montoItem'] =  line._get_price_total_and_subtotal()['price_total']
            lines.append(vals)
        return lines

    def _get_descuentos(self, invoice_line_ids):
        lines = []
        for line in invoice_line_ids:
            vals = {}
            vals['indicadorFacturacion'] = line.uy_invoice_indicator
            vals['descripcion'] = line.name[:80]
            if line.move_id.uy_gross_amount == '1':
                vals['monto'] = abs(line.price_total)
            else:
                vals['monto'] = abs(line.price_subtotal)
            lines.append(vals)
        return lines
    def _get_ref(self, invoice_id):
        vals = {}
        vals['referenciaGlobal'] = (invoice_id.reversed_entry_id or invoice_id.debit_origin_id) and 0 or 1
        vals['referencia'] = invoice_id.ref
        if invoice_id.uy_document_code in ['102', '112', '122']:
            vals['descripcion'] = invoice_id.ref or invoice_id.invoice_line_ids[0].name[:80] or ''
            vals['tipoDocRef'] = invoice_id.reversed_entry_id.uy_document_code or ''
            if invoice_id.reversed_entry_id.uy_cfe_serie:
                vals['serie'] = invoice_id.reversed_entry_id.uy_cfe_serie or ''
            else:
                vals['serie'] = invoice_id.name.split("-")[0]
            if invoice_id.reversed_entry_id.uy_cfe_number:
                vals['numero'] = invoice_id.reversed_entry_id.uy_cfe_number or ''
            else:
                vals['numero'] = invoice_id.name.split("-")[-1]
            vals['fechaCFEref'] = invoice_id.reversed_entry_id.invoice_date.strftime("%Y-%m-%d")
        else:
            vals['descripcion'] = invoice_id.ref or invoice_id.invoice_line_ids[0].name[:80] or ''
            vals['tipoDocRef'] = invoice_id.debit_origin_id.uy_document_code or ''
            vals['serie'] = invoice_id.debit_origin_id.uy_cfe_serie or ''
            vals['numero'] = invoice_id.debit_origin_id.uy_cfe_number or ''
            vals['fechaCFEref'] = invoice_id.debit_origin_id.invoice_date.strftime("%Y-%m-%d")
        return [vals]
        
        
    def send_einvoice(self, batch_id):
        vals = {}
        vals.update(self.get_sobre(batch_id))
        vals['servidor'] = self.get_server(batch_id.move_id)
        documento = {}

        documento.update(self._get_voucher(batch_id.move_id))
        documento['emisor'] = self._get_company(batch_id.move_id)
        if batch_id.move_id.company_id.uy_server == 'factura_express':
            documento['serie'] = batch_id.move_id.name.replace('ANNUL/', '').split('-')[0]
            documento['numero'] = batch_id.move_id.name.replace('ANNUL/', '').split('-')[-1]
        documento['adquirente'] = self._get_partner(batch_id.move_id)
        documento.update(self._get_total(batch_id.move_id))
        documento['items'] = self._get_lines(batch_id.move_id.invoice_line_ids.filtered(lambda s: s.price_subtotal>0.0))
        documento['descuentos'] = self._get_descuentos(batch_id.move_id.invoice_line_ids.filtered(lambda s: s.price_subtotal < 0.0))
        documento['montosBrutos']= batch_id.move_id.uy_gross_amount
        documento['adenda'] = batch_id.move_id.narration and \
                              str(batch_id.move_id.narration).replace('<br>', '\n').replace('<br />', '\n'). \
                                  replace('<p>', '').replace('</p>', '\n') or ""
        vals['documento'] = documento
        if batch_id.move_id.uy_document_code in ['102', '103', '112', '113', '122', '123']:
            documento['referencias'] = self._get_ref(batch_id.move_id)
        res = Sobre(vals).enviarCFE()
        return res

    def get_cfe_pdf(self, move, batch_id=False):
        if not batch_id:
            batch_ids = move.edi_document_ids.filtered(
                lambda s: s.edi_format_id.code == 'edi_uy_cfe' and s.uy_biller_id != False)
            batch_id = len(batch_ids) > 1 and batch_ids[0] or batch_ids
        if batch_id:
            if move.company_id.uy_server == 'biller':
                try:
                    vals = {}
                    vals['servidor'] = self.get_server(batch_id.move_id)
                    if batch_id.uy_cfe_id:
                        pdf_data = Sobre(vals).obtenerPdfCFE(batch_id.uy_cfe_id)
                        return pdf_data
                    else:
                        return {}
                except Exception:
                    return {'estado': False, 'respuesta': {'error': 'Error en la consulta a biller'}}
            elif move.company_id.uy_server == 'factura_express':
                try:
                    vals = {}
                    vals['servidor'] = self.get_server(batch_id.move_id)
                    if batch_id.uy_invoice_url:
                        pdf_data = Sobre(vals).obtenerPdfCFE(batch_id.uy_invoice_url)
                        return pdf_data
                    else:
                        return {}
                except Exception:
                    return {'estado': False, 'respuesta': {'error': 'Error en la consulta a Factura Express'}}
        else:
            return {'estado': False, 'respuesta': {'error': 'No existe hash de consulta'}}

    def get_cfe_invoice_status(self, move_id, batch_id=None):
        if not batch_id:
            batch_ids = move_id.edi_document_ids.filtered(
                lambda s: s.edi_format_id.code == 'edi_uy_cfe' and s.uy_biller_id != False)
            batch_id = len(batch_ids) > 1 and batch_ids[0] or batch_ids
        if batch_id:
            try:
                vals = {}
                vals['servidor'] = self.get_server(batch_id.move_id)
                if batch_id.uy_cfe_id:
                    invoice_data = Sobre(vals).obtenerEstadoCFE(batch_id.uy_cfe_id)
                    return len(invoice_data) and invoice_data[0] or {}
                else:
                    return {}
            except Exception:
                return {'estado': False, 'respuesta': {'error': 'Error en la consulta a biller'}}
        else:
            return {'estado': False, 'respuesta': {'error': 'No existe hash de consulta'}}