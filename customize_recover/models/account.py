
from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    alien_vat = fields.Char()