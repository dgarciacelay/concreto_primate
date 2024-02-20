# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

import json
from odoo import fields, api, models, _
from odoo.exceptions import UserError


class srAccountMove(models.Model):
    _inherit = "account.move"

    def _compute_payments_widget_to_reconcile_info(self):
        for move in self:
            move.invoice_outstanding_credits_debits_widget = json.dumps(False)
            move.invoice_has_outstanding = False

            if (
                move.state != "posted"
                or move.payment_state not in ("not_paid", "partial")
                or not move.is_invoice(include_receipts=True)
            ):
                continue

            pay_term_lines = move.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type
                in ("receivable", "payable")
            )

            domain = [
                ("account_id", "in", pay_term_lines.account_id.ids),
                ("move_id.state", "=", "posted"),
                ("partner_id", "=", move.commercial_partner_id.id),
                ("reconciled", "=", False),
                "|",
                ("amount_residual", "!=", 0.0),
                ("amount_residual_currency", "!=", 0.0),
            ]

            payments_widget_vals = {
                "outstanding": True,
                "content": [],
                "move_id": move.id,
            }

            if move.is_inbound():
                domain.append(("balance", "<", 0.0))
                payments_widget_vals["title"] = _("Outstanding credits")
            else:
                domain.append(("balance", ">", 0.0))
                payments_widget_vals["title"] = _("Outstanding debits")

            for line in self.env["account.move.line"].search(domain):

                if line.currency_id == move.currency_id:
                    # Same foreign currency.
                    amount = abs(line.amount_residual_currency)
                else:
                    # Different foreign currencies.
                    amount = move.company_currency_id._convert(
                        abs(line.amount_residual),
                        move.currency_id,
                        move.company_id,
                        line.date,
                    )

                if move.currency_id.is_zero(amount):
                    continue

                payments_widget_vals["content"].append(
                    {
                        "journal_name": line.ref or line.move_id.name,
                        "move_type": move.move_type,
                        "amount": amount,
                        "currency": move.currency_id.symbol,
                        "id": line.id,
                        "move_id": line.move_id.id,
                        "position": move.currency_id.position,
                        "digits": [69, move.currency_id.decimal_places],
                        "payment_date": fields.Date.to_string(line.date),
                    }
                )

            if not payments_widget_vals["content"]:
                continue

            move.invoice_outstanding_credits_debits_widget = json.dumps(
                payments_widget_vals
            )
            move.invoice_has_outstanding = True

    def js_remove_outstanding_partial(self, partial_id):
        """Called by the 'payment' widget to remove a reconciled entry to the present invoice.

        :param partial_id: The id of an existing partial reconciled with the current invoice.
        """
        self.ensure_one()
        partial = self.env["account.partial.reconcile"].browse(partial_id)

        line = self.line_ids.filtered(
            lambda l: l.move_id.id == partial.credit_move_id.move_id.id
            and l.account_id.id == partial.credit_move_id.account_id.id
            and not l.partial_matching_number
        )
        if line and len(line.ids) > 1:
            line = line[-1]

        credit_partial_matching_number = partial.credit_move_id.partial_matching_number
        if not credit_partial_matching_number:
            return partial.unlink()

        debit_partial_matching_number = (
            partial.debit_move_id.partial_matching_number.split(",")
        )
        if len(debit_partial_matching_number) > 1:
            debit_partial_matching_number = (
                ",".join(number)
                for number in debit_partial_matching_number
                if credit_partial_matching_number != number
            )
            partial.credit_move_id.write(
                {"partial_matching_number": credit_partial_matching_number}
            )
        else:
            partial.credit_move_id.write({"partial_matching_number": ""})

        val_list = []
        val_list.append(
            (
                1,
                partial.credit_move_id.id,
                {
                    "debit": 0.0,
                    "credit": 0.0,
                    "amount_currency": -0.0,
                },
            )
        )
        val_list.append(
            (
                1,
                line.id,
                {
                    "debit": 0.0,
                    "credit": line.credit + partial.credit_move_id.credit,
                    "amount_currency": -(line.credit + partial.credit_move_id.credit),
                },
            )
        )
        partial.credit_move_id.payment_id.move_id.write({"line_ids": val_list})
        credit_line = partial.credit_move_id
        partial = partial.unlink()
        credit_line.with_context({"force_delete": True}).unlink()
        return partial


class srAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    partial_matching_number = fields.Char(
        string="Partial Matching #",
        compute="_compute_matching_number",
        store=True,
        help="Partial Matching number for this line, 'PM' if it is only partially reconcile, or the name of the full reconcile if it exists.",
    )

    def _check_reconciliation(self):
        for line in self:
            if (
                not line.payment_id.sr_is_partial
                and line.matched_debit_ids
                or not line.payment_id.sr_is_partial
                and line.matched_credit_ids
            ):
                raise UserError(
                    _(
                        "You cannot do this modification on a reconciled journal entry. "
                        "You can just change some non legal fields or you must unreconcile first.\n"
                        "Journal Entry (id): %s (%s)"
                    )
                    % (line.move_id.name, line.move_id.id)
                )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
