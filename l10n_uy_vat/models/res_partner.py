# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from math import floor
import logging
_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = 'res.partner'
    
    
    @api.model
    def _get_uy_doc_type(self):
        res = []
        res.append(('2','RUT'))
        res.append(('3','C.I.'))
        res.append(('4','Otros'))
        res.append(('5','Pasaporte'))
        res.append(('6','DNI'))
        return res

    uy_doc_type= fields.Selection(selection=_get_uy_doc_type, string="Document Type")
    uy_tradename = fields.Char("Tradename")
    
    @api.constrains("vat")
    def check_uy_doc_number(self):
        for partner in self:
            if partner.country_code != 'UY':
                continue
            if not partner.uy_doc_type and not partner.vat:
                continue
            elif not partner.uy_doc_type and partner.vat and not partner.parent_id:
                raise ValidationError(_("Select a document type"))
            elif partner.uy_doc_type and not partner.vat:
                raise ValidationError(_("Enter the document number"))
            vat = partner.vat
            if partner.uy_doc_type == '2':
                check = self._validate_rut(vat)
                if not check:
                    _logger.info("The VAT Number [%s] is not valid !" % vat)
                    raise ValidationError(_('the RUT entered is incorrect'))
            elif partner.uy_doc_type == '3':
                check = self._validate_ci(vat)
                if not check:
                    _logger.info("The CI Number [%s] is not valid !" % vat)
                    raise ValidationError(_('the RUT entered is incorrect'))
            else:
                continue
    
    @staticmethod
    def _validate_rut(vat):
        factor = '43298765432'
        sum = 0
        dig_check = None
        if len(vat) != 12:
            return False
        try:
            int(vat)
        except ValueError:
            return False 
        for f in range(0,11):
            sum += int(factor[f]) * int(vat[f])
        subtraction = 11 - floor((sum % 11))
        if subtraction < 10:
            dig_check = subtraction
        elif subtraction == 10:
            dig_check = ""
        elif subtraction == 11:
            dig_check = 0

        if not int(vat[11]) == dig_check:
            return False
        return True

    @staticmethod
    def _validate_ci(vat):
        vat=vat.replace("-","").replace('.','')
        sum=0
        if not vat:
            return False
        try:
            int(vat)
        except ValueError:
            return False 
        vat = "%08d" % int(vat)
        long = len(vat)
        if long>8:
            return False
        code = [2, 9, 8, 7, 6, 3, 4]
        for f in range(0,long-1):
            sum += int(vat[f]) * int(code[f])
        total = sum + int(vat[-1])
        subtraction = total%10
        if subtraction!=0:
            return False
        return True
    
    # @api.onchange('company_type')
    # def onchange_company_type(self):
        # self.pe_doc_type= self.company_type == 'company' and "6" or "1"
        # super(Partner, self).onchange_company_type()
        #
    # @api.onchange('uy_doc_type')
    # def onchange_uy_doc_type(self):
        # if self.uy_doc_type =="2":
            # self.company_type = 'company'
        # else:
            # self.company_type = 'person'
            #

    
    