# Copyright 2009 Camptocamp
# Copyright 2009 Grzegorz Grzelak
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# 2020 Tupaq 
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict
from datetime import timedelta, datetime
import re
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from pysimplesoap.client import SoapClient
import requests
import logging

_logger = logging.getLogger(__name__)

BCU_CURRENCIES = {
    "ARS": 500, "BRL": 1000, "CAD": 2309, "CLP": 1300, "CNH": 4155, "CNY": 4150,
    "COP": 5500, "DKK": 1800, "USD": 2222, "HKD": 5100, "HUF": 4300, "INR": 5700,
    "ISK": 4900, "JPY": 3600, "KRW": 5300, "MYR": 5600, "MXN": 4200, "NOK": 4600,
    "PYG": 4800, "PEN": 4000, "RUB": 5400, "ZAR": 1620, "SEK": 5800, "CHF": 5900,
    "TRY": 4400, "VEF": 6200, "AUD": 105, "GBP": 2700, "NZD": 1490, "EUR": 1111,
    "SDR": 2
}

ISO_CURRENCIES = {
    500: "ARS", 1000: "BRL", 2309: "CAD", 1300: "CLP", 4155: "CNH", 4150: "CNY",
    5500: "COP", 1800: "DKK", 2222: "USD", 5100: "HKD", 4300: "HUF", 5700: "INR",
    4900: "ISK", 3600: "JPY", 5300: "KRW", 5600: "MYR", 4200: "MXN", 4600: "NOK",
    4800: "PYG", 4000: "PEN", 5400: "RUB", 1620: "ZAR", 5800: "SEK", 5900: "CHF",
    4400: "TRY", 6200: "VEF", 105: "AUD", 2700: "GBP", 1490: "NZD", 1111: "EUR",
    2: "SDR"
}


class ResCurrencyRateProviderSUNAT(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[('BCU', 'Central Bank of Uruguay')],
        ondelete={"BCU": "set default"},
    )
    uy_accounting_rate = fields.Boolean("Uruguayan Accounting Rate",
                                        help="Change the exchange rate date to the next day")

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != 'BCU':
            return super()._get_supported_currencies()  # pragma: no cover
        return \
            [
                "ARS", "BRL", "CAD", "CLP", "CNH", "CNY", "COP", "DKK", "USD", "HKD",
                "HUF", "INR", "ISK", "JPY", "KRW", "MYR", "MXN", "NOK", "PYG", "PEN",
                "RUB", "ZAR", "SEK", "CHF", "VEF", "AUD", "GBP", "NZD", "EUR", "SDR",
            ]

    def _currency_by_bcu_code(self, currency_array):
        currency_codes = []
        for currency in currency_array:
            bcu_code = BCU_CURRENCIES.get(currency)
            if bcu_code:
                currency_codes.append({"item": bcu_code})
        return currency_codes

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        if self.service != 'BCU':
            return super()._obtain_rates(base_currency, currencies, date_from,
                                         date_to)  # pragma: no cover
        self.ensure_one()
        if base_currency not in ['UYU']:  # pragma: no cover
            raise UserError(_(
                'Central Bank of Uruguay is suitable only for companies'
                ' with UYU as base currency!'
            ))

        days = date_to - date_from
        if days.days < 0:
            raise UserError(_('The end date must be greater than the date from'))

        res = defaultdict(dict)

        try:
            client = SoapClient(wsdl="https://cotizaciones.bcu.gub.uy/wscotizaciones/servlet/awsultimocierre?wsdl",
                                cache=None, ns='cot', soap_ns='soapenv', soap_server="jetty", trace=True)
            rate_date = client.Execute()
            date = rate_date.get('Salida', {}).get('Fecha')
            # if (context_today.date()-date).days != 0:
            #    date = False
            _logger.debug("BCU currency date service : connecting...")
        except Exception:
            msj = "BCU currency date service : not connected"
            _logger.debug(msj)
            return res
        if date_from > date:
            date_from = date
        days = date_to - date
        if date_to > date:
            date_to = date  # raise UserError(_('The end date must be greater than the date from'))

        quotes = []
        currencies_datas = {}
        try:
            client = SoapClient(wsdl="https://cotizaciones.bcu.gub.uy/wscotizaciones/servlet/awsbcucotizaciones?wsdl",
                                cache=None, namespace='Cotiza', ns='cot', soap_ns='soapenv', soap_server="jbossas6",
                                trace=True)
            currencies_codes = self._currency_by_bcu_code(currencies)
            response = client.Execute(
                Entrada={'Moneda': currencies_codes, 'FechaDesde': date_from, "FechaHasta": date_to, 'Grupo': 0})
            _logger.debug("BCU currency rate service : connecting...")
            quotes = response.get("Salida", {}).get("datoscotizaciones", {}).get("datoscotizaciones.dato")
            for quote in quotes:
                code = ISO_CURRENCIES.get(quote.get('Moneda'))
                if not code in currencies:
                    continue
                if self.uy_accounting_rate:
                    date = fields.Date.to_string(quote.get('Fecha') + timedelta(days=1))
                else:
                    date = fields.Date.to_string(quote.get('Fecha'))
                rate = quote.get("TCV", 1.0)
                res[date][code] = 1 / rate
            return res
        except Exception:
            msj = "BCU currency rate service : not connected"
            _logger.debug(msj)

        # Web service de respaldo
        if not res:
            headers = {}
            headers['Content-Type'] = 'application/json'
            url = "https://www.bcu.gub.uy/_layouts/15/BCU.Cotizaciones/handler/CotizacionesHandler.ashx?op=getcotizaciones"
            currency_codes = []
            for currency in currencies:
                bcu_code = BCU_CURRENCIES.get(currency)
                if bcu_code:
                    currency_codes.append({"Val": bcu_code, "Text": bcu_code})
            if (date_to - date_from).days >= 30:
                msj = "The date range is greater than 30 days"
                _logger.debug(msj)
                return res
            data = {
                "KeyValuePairs":
                    {
                        "Monedas": currency_codes,
                        "FechaDesde": date_from.strftime('%d/%m/%Y'),
                        "FechaHasta": date_to.strftime('%d/%m/%Y'),
                        "Grupo": "0"
                    }
            }
            try:
                response = requests.post(url, json=data, headers=headers)
                _logger.debug(response.text)
                quotes = response.json().get('cotizacionesoutlist', {}).get('Cotizaciones', [])
                for quote in quotes:
                    code = ISO_CURRENCIES.get(quote.get('Moneda'))
                    if not code in currencies:
                        continue
                    str_date = re.findall(".(\d+).", quote.get('Fecha'))
                    if str_date:
                        if self.uy_accounting_rate:
                            date = fields.Date.to_string(
                                datetime.fromtimestamp(int(str_date[0]) / 1000.0) + timedelta(days=1))
                        else:
                            date = fields.Date.to_string(datetime.fromtimestamp(int(str_date[0]) / 1000.0))
                        rate = quote.get("TCV", 1.0)
                        res[date][code] = 1 / rate

            except Exception:
                msj = "BCU currency rate service : not connected"
                _logger.debug(msj)
        return res


