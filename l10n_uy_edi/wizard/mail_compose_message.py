# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'
    
        
    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        res = super(MailComposer, self).onchange_template_id(template_id=template_id, composition_mode=composition_mode, 
                                                             model=model, res_id=res_id)
        def_attachment_ids = self.env.context.get('default_attachment_ids')
        if def_attachment_ids:
            value = res.get('value')
            attachment_ids = value.get('attachment_ids',[])
            attach_ids = []
            if attachment_ids:
                attach_ids = attachment_ids[0][2] + def_attachment_ids[0][2]
            else:
                attach_ids = def_attachment_ids[0][2]
            value['attachment_ids'] =[(6,0, attach_ids)] 
            res['value'] = value
        return res