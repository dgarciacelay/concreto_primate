# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'
    
    def _prepare_default_reversal(self, move):
        res = super(AccountMoveReversal, self)._prepare_default_reversal(move)
        journal_id = res.get('journal_id')
        res['journal_id'] = move.journal_id.uy_credit_note_id.id or journal_id
        uy_document_code = move.journal_id.uy_credit_note_id.uy_document_code or {'101':'102','111':'112'}.get(move.uy_document_code, False)
        res['uy_document_code'] = uy_document_code
        return res

    