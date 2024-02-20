# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountDebitNote(models.TransientModel):

    _inherit = 'account.debit.note'

    def _prepare_default_values(self, move):
        res = super(AccountDebitNote, self)._prepare_default_values(move)
        journal_id = res.get('journal_id')
        res['journal_id'] = move.journal_id.uy_dedit_note_id.id or journal_id
        uy_document_code = move.journal_id.uy_dedit_note_id.uy_document_code or {'102':'103','112':'113'}.get(move.uy_document_code, False)
        res['uy_document_code'] = uy_document_code
        return res