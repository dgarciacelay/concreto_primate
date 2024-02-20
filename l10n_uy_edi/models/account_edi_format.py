# -*- coding: utf-8 -*-

from odoo import api, models, fields, tools, _
import logging
from base64 import decodebytes
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _get_move_applicability(self, move):
        self.ensure_one()
        res = super(AccountEdiFormat, self)._get_move_applicability(move)
        if self.code != 'edi_uy_cfe':
            return res
        res = {
            'post': self._uy_post_cfe,
            #'cancel': self._uy_cancel_cfe,
            #'edi_content': self._uy_pdf_cfe,
        }
        return res

    def _uy_post_cfe(self, move):
        move_result = self.env['uy.edi.send.cfe'].send_einvoice(move.uy_cfe_id)
        values = {}
        res_values = {}
        if move_result.get('estado'):
            if move.company_id.uy_server == 'efactura':
                data = move_result.get('respuesta', {})
                if data.get('PDFcode'):
                    attachment_id = self.env['ir.attachment'].create({
                        'name': "%s-%s.pdf" % (data.get('serie', ''), data.get('numero', '')),
                        'datas': data.get('PDFcode').encode('utf-8'),
                        'mimetype': 'application/pdf'
                    })
                else:
                    attachment_id = False
                if attachment_id:
                    res_values['attachment'] = attachment_id
                if data.get('QRcode'):
                    uy_qr_id = self.env['ir.attachment'].create({
                        'name': "%s-%s.png" % (data.get('serie', ''), data.get('numero', '')),
                        'datas': data.get('PDFcode').encode('utf-8'),
                        'mimetype': 'image/png'
                    })
                else:
                    uy_qr_id = False
                values.update({
                    'name': "%s-%s" % (data.get('serie', ''), data.get('numero', '')),
                    'uy_cfe_serie': data.get('serie', False),
                    'uy_cfe_number': data.get('numero', False),
                    'uy_qr_id': uy_qr_id,
                    'uy_security_code': data.get('codigoSeg', False),
                    'uy_constancy': data.get('CAE', False),
                    'uy_constancy_serie': data.get('CAEserie', False),
                    'uy_constancy_from': data.get('CAEdesde', False),
                    'uy_constancy_to': data.get('CAEhasta', False),
                    'uy_url_code': data.get('URLcode', False),
                    # 'error': data.get('codigosError'),
                    # 'blocking_level': 'error' if 'codigosError' in move_result else False,
                })
                if not data.get('codigosError'):
                    res_values['success'] = True
                else:
                    error = data.get('codigosError').split(',')[0]
                    if self.env['uy.datas'].search([('data_code', '=', 'UY.EFACTURA.ERROR'), ('code', '=', error)]):
                        values.update({'uy_error_code': error})
                    res_values['error'] = data.get('codigosError')
                    move.message_post(body=_('Error.<br/> %s') % data.get('codigosError'))
                if data.get('PDFcode', ''):
                    move.message_post(body=_('Sending the electronic document succeeded.<br/>'),
                                      attachments=[("%s-%s.pdf" % (
                                          data.get('serie', ''), data.get('numero', '')),
                                                    decodebytes(data.get('PDFcode', '').encode('utf-8')))])
                    move.uy_print = True
            if move.company_id.uy_server == 'factura_express':
                data = move_result.get('respuesta', {})
                if data.get('pdf_document'):
                    attachment_id = self.env['ir.attachment'].create({
                        'name': "%s-%s.pdf" % (data.get('serie', ''), data.get('numero', '')),
                        'datas': data.get('pdf_document').encode('utf-8'),
                        'mimetype': 'application/pdf'
                    })
                else:
                    attachment_id = False
                if attachment_id:
                    res_values['attachment'] = attachment_id
                # if data.get('QRcode'):
                #     uy_qr_id = self.env['ir.attachment'].create({
                #         'name': "%s-%s.png" % (data.get('serie', ''), data.get('numero', '')),
                #         'datas': data.get('PDFcode').encode('utf-8'),
                #         'mimetype': 'image/png'
                #     })
                # else:
                uy_qr_id = False

                values.update({
                    'name': "%s-%s" % (data.get('serie', ''), data.get('numero', '')),
                    'uy_cfe_serie': data.get('serie', False),
                    'uy_cfe_number': data.get('numero', False),
                    'uy_qr_id': uy_qr_id,
                    'uy_security_code': data.get('codigoSeg', False),
                    'uy_constancy': data.get('id', False),
                    # 'uy_constancy_serie': data.get('CAEserie', False),
                    'uy_constancy_from': data.get('dNro', False),
                    'uy_constancy_to': data.get('hNro', False),
                    'uy_url_code': data.get('qrText', False),
                    'uy_invoice_url': data.get('linkDocumento'),
                    # 'error': data.get('codigosError'),
                    # 'blocking_level': 'error' if 'codigosError' in move_result else False,
                })
                if data.get('codigo_retorno','') == '00':
                    res_values['success'] = True
                else:
                    # error = data.get('codigosError').split(',')[0]
                    # if self.env['uy.datas'].search([('data_code', '=', 'UY.EFACTURA.ERROR'), ('code', '=', error)]):
                    #     values.update({'uy_error_code': error})
                    res_values['error'] = _('Error: %s') % data.get('codigo_retorno')
                    move.message_post(body=_('Error code: %s <br/>Error: %s') % (data.get('codigo_retorno'), values.get('error')))
                if data.get('pdf_document', ''):
                    move.message_post(
                        body=_('Sending the electronic document succeeded.<br/>%s') % data.get('mensaje_retorno', ''),
                        attachments=[("%s-%s.pdf" % (
                            data.get('serie', ''), data.get('numero', '')),
                                      decodebytes(data.get('pdf_document', '').encode('utf-8')))])
                    move.uy_print = True
                else:
                    if data.get('linkDocumento', ''):
                        move.message_post(body=_(
                            'Sending the electronic document succeeded.<br/><a ref="%s" title="" target="_blank">Show Invoice</a>' % data.get(
                                'linkDocumento', '')))

            elif move.company_id.uy_server == 'biller':
                data = move_result.get('respuesta', {})
                if data.get('pdf'):
                    attachment_id = self.env['ir.attachment'].create({
                        'name': "%s-%s.pdf" % (data.get('serie', ''), data.get('numero', '')),
                        'datas': data.get('pdf').encode('utf-8'),
                        'mimetype': 'application/pdf'
                    })
                else:
                    attachment_id = False
                if attachment_id:
                    res_values['attachment'] = attachment_id
                values.update({
                    'name': "%s-%s" % (data.get('serie', ''), data.get('numero', '')),
                    #'attachment_id': attachment_id,
                    'uy_cfe_serie': data.get('serie', False),
                    'uy_cfe_number': data.get('numero', False),
                    'uy_cfe_hash': data.get('hash', False),
                    'uy_cfe_id': data.get('id'),
                    'uy_constancy': data.get('cae', {}).get('numero', False),
                    'uy_constancy_serie': data.get('cae', {}).get('serie', False),
                    'uy_constancy_from': data.get('cae', {}).get('inicio') and str(
                        data.get('cae', {}).get('inicio')) or False,
                    'uy_constancy_to': data.get('cae', {}).get('fin') and str(
                        data.get('cae', {}).get('fin')) or False,
                    'uy_constancy_vto': data.get('cae', {}).get('fecha_expiracion', False),
                    'uy_security_code': data.get('hash', False) and data.get('hash', False)[-6:] or False
                    # 'blocking_level': 'error' if 'codigosError' in move_result else False,
                })
                if move.company_id.uy_verification_url:
                    date = move.invoice_date.strftime('%d/%m/%Y')
                    string = "%sconsultaQR/cfe?%s,%s,%s,%s,%s,%s,%s" % (move.company_id.uy_verification_url,
                                                                        move.company_id.vat,
                                                                        move.uy_document_code,
                                                                        values.get('uy_cfe_serie'),
                                                                        values.get('uy_cfe_number'),
                                                                        move.amount_total, date,
                                                                        values.get('uy_biller_hash'))
                    values['uy_url_code'] = string

                if not values.get('error'):
                    res_values['success'] = True
                else:
                    error = values.get('error').split(',')[0]
                    # raise ValidationError(values.get('error'))
                    if self.env['uy.datas'].search(
                            [('data_code', '=', 'UY.BILLER.ERROR'), ('code', '=', error)]):
                        values.update({'uy_error_code': error})
                    res_values['error'] = data.get('codigosError')
                    move.message_post(body=_('Error.<br/> %s') % data.get('codigosError'))
                    values.update({'state': 'to_cancel'})
                # document.write(values)
                # if not old_attachment.res_model or not old_attachment.res_id:
                #     attachments_to_unlink |= old_attachment
                if data.get('pdf', ''):
                    move.message_post(body=_('Sending the electronic document succeeded.<br/>'),
                                      attachments=[("%s-%s.pdf" % (
                                          data.get('serie', ''), data.get('numero', '')),
                                                    decodebytes(data.get('pdf', '').encode('utf-8')))])
                    move.uy_print = True
            # document.write(values)
        else:
            if move_result.get('respuesta', {}):
                error = str(move_result.get('respuesta'))
            else:
                error = str(move_result)
            res_values['error'] = error
            move.message_post(body=_('Error.<br/> %s') % error)
        if values and move.uy_cfe_id:
            move.uy_cfe_id.write(values)
        return {move: res_values}

    def _is_compatible_with_journal(self, journal):
        self.ensure_one()
        res = super()._is_compatible_with_journal(journal)
        if self.code != 'edi_uy_cfe':
            return res
        return journal.type == 'sale'

    def _needs_web_services(self):
        self.ensure_one()
        res = super()._needs_web_services()
        if self.code != 'edi_uy_cfe':
            return res
        return True

    # def _export_uy_cfe(self, document, test_mode=False):
    #     self.ensure_one()
    #     if self.code == 'edi_uy_cfe':
    #         res = self.env['uy.edi.send.cfe'].send_einvoice(document)
    #         return {document.move_id:res}
    #     else:
    #         return super()._export_uy_cfe(document, test_mode=test_mode)

    def _check_move_configuration(self, move):
        self.ensure_one()
        if self.code != 'edi_uy_cfe':
            return super(AccountEdiFormat, self)._check_move_configuration(move)
        res = []
        company_id = move.company_id
        if not company_id.uy_server:
            res.append(_("The type of server is required"))
        if not company_id.uy_server_url:
            res.append(_("The server url is required"))
        if company_id.uy_server in ['efactura']:
            if not company_id.uy_username:
                res.append(_("The server username is required"))
        if not company_id.uy_password:
            res.append(_("The server password is required"))

        if move.journal_id.uy_document_code not in ['101', '102', '103', '111', '112', '113', '121', '122', '123']:
            res.append("Documento no soportado, solo es posible emitir eFacturas, eTickets, Notas de Credito y Debito")
        if move.uy_document_code != move.journal_id.uy_document_code:
            res.append("El codigo de documento debe ser igual al codigo de documento del diario")
        if move.uy_document_code in ['121', '122', '123'] and move.invoice_line_ids.filtered(lambda s: s.uy_invoice_indicator != '10'):
            res.append("Todos los items del comprobante deben tener el tipo de Indicador de Factura como 'Exportacion y Asimiladas cod: 10'")
        return res