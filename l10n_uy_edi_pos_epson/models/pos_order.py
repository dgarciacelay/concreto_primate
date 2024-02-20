# -*- coding: utf-8 -*-
from odoo import api, fields, models
from pdf2image import convert_from_bytes
from PIL import Image
from base64 import decodebytes, encodebytes
from io import BytesIO

class PosOrder(models.Model):
    _inherit = 'pos.order'
    

    def get_uy_pdf_invoice(self):
        self.ensure_one()
        # vals = {}
        # move_id = self.account_move.sudo()
        # if not move_id.uy_print:
        #     move_id.action_check_cfe_pdf_status()
        # edi_document_id = move_id.uy_cfe_id
        # if edi_document_id.attachment_id:
        #     vals['url'] = '/web/content/ir.attachment/%d/datas/%s' % (edi_document_id.attachment_id.id, edi_document_id.attachment_id.name)
        # if edi_document_id.error:
        #     vals['error'] = edi_document_id.error
        res = super().get_uy_pdf_invoice()
        move_id = self.account_move.sudo()
        edi_document_id = move_id.uy_cfe_id
        if edi_document_id.attachment_id:
            images = convert_from_bytes(decodebytes(edi_document_id.attachment_id.datas))
            all_images = []
            # Proecess image
            for i in range(len(images)):
                # image = Image.frombytes(images[i])
                grayscale = images[i].convert('L')
                # BW = image.convert('1')
                file = BytesIO()
                grayscale.save(file,'png')
                image_b64 = encodebytes(file.getvalue())
                width = grayscale.width % 2 != 0 and grayscale.width+1 or grayscale.width
                all_images.append(
                    {
                        'image': image_b64,
                        'height': grayscale.height,
                        'width': width
                    }
                )
            res['images'] = all_images
        return res
    
    
