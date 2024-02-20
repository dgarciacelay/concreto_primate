# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import fields, api, models, _


class srPartialPaymentWizard(models.TransientModel):
    _name = "partial.payment.wizard"
    _description = "Partial Payment Wizard"

    @api.model
    def default_get(self, fields):
        res = super(srPartialPaymentWizard, self).default_get(fields)
        move_id = self.env["account.move"].browse(self.env.context["active_id"])
        line_id = self.env["account.move.line"].browse(self.env.context["line_id"])
        if move_id:
            res["move_id"] = move_id.id
            res["move_line_id"] = line_id.id
            res["amount_total"] = line_id.payment_id.amount
            res["amount_due"] = move_id.amount_residual
            res["currency_id"] = move_id.currency_id.id
            res["payment_id"] = line_id.payment_id.id
            res["company_id"] = move_id.company_id.id
            res["company_currency_id"] = move_id.company_currency_id.id
            res["remaining_amount_for_payment"] = line_id.payment_id.amount
            res["remaining_amount_for_invoice"] = move_id.amount_residual
        return res

    move_id = fields.Many2one(comodel_name="account.move", string="Account Move")
    move_line_id = fields.Many2one(
        comodel_name="account.move.line", string="Account Move Line"
    )
    amount_total = fields.Monetary(string="Amount Total")
    amount_due = fields.Monetary(string="Amount Due")
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency")
    payment_id = fields.Many2one(comodel_name="account.payment", string="Payment")
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Company Currency",
    )
    amount_to_pay = fields.Monetary(string="Amount to Pay")
    remaining_amount_for_payment = fields.Monetary(
        compute="compute_remaining_amount", string="Remaining Amount For Payment"
    )
    remaining_amount_for_invoice = fields.Monetary(
        compute="compute_remaining_amount", string="Remaining Amount For Invoice"
    )

    @api.depends("amount_to_pay")
    def compute_remaining_amount(self):
        for payment in self:
            payment.remaining_amount_for_payment = (
                payment.amount_total - payment.amount_to_pay
            )
            payment.remaining_amount_for_invoice = (
                payment.amount_due - payment.amount_to_pay
            )

    def register_payment(self):
        self.ensure_one()
        line_id = self.move_line_id
        if line_id.payment_id.partner_type == "customer":
            vals_list = []
            vals_list.append(
                (
                    0,
                    0,
                    {
                        "account_id": line_id.account_id.id,
                        "partner_id": line_id.partner_id.id,
                        "name": line_id.move_name,
                        "amount_currency": -self.amount_to_pay,
                        "currency_id": line_id.currency_id.id,
                        "debit": 0.0,
                        "credit": self.amount_to_pay,
                        "tax_ids": [(6, 0, line_id.tax_ids.ids)],
                        "date_maturity": line_id.date_maturity,
                    },
                )
            )
            vals_list.append(
                (
                    1,
                    line_id.id,
                    {
                        "debit": 0.0,
                        "credit": line_id.credit - self.amount_to_pay,
                        "amount_currency": -(line_id.credit - self.amount_to_pay),
                    },
                )
            )
            self.payment_id.write({"sr_is_partial": True})
            self.payment_id.move_id.write({"line_ids": vals_list})

            partial_sequence = (
                self.env["ir.sequence"].next_by_code("account.move.line") or ""
            )
            lines = self.payment_id.move_id.line_ids.filtered(
                lambda l: l.credit == self.amount_to_pay
                and l.move_id.id == self.payment_id.move_id.id
            )
            if lines and not lines[-1].partial_matching_number:
                lines[-1].write({"partial_matching_number": partial_sequence})
            if lines:
                move_line = self.move_id.line_ids.filtered(
                    lambda l: l.credit != self.amount_to_pay
                    and l.account_id.id == lines[-1].account_id.id
                    and l.move_id.id == self.move_id.id
                )
                if move_line and not move_line.partial_matching_number:
                    move_line.write({"partial_matching_number": partial_sequence})
                elif move_line and move_line.partial_matching_number:
                    move_line.write(
                        {
                            "partial_matching_number": "%s,%s"
                            % (move_line.partial_matching_number, partial_sequence)
                        }
                    )
            lines += move_line
            lines.reconcile()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: