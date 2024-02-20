odoo.define('l10n_uy_edi_pos_epson.PosResReceiptScreen', function (require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');
    const { nextFrame } = require('point_of_sale.utils');

    const PosResReceiptScreen = (ReceiptScreen) =>
        class extends ReceiptScreen {
            async _uy_printReceipt(images) {
                if (this.env.proxy.printer) {
                    const printResult = await this.env.proxy.printer.print_pdf_receipt(images);
                    if (printResult.successful) {
                        return true;
                    } else {
                        await this.showPopup('ErrorPopup', {
                            title: printResult.message.title,
                            body: printResult.message.body,
                        });
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            title: printResult.message.title,
                            body: 'Do you want to print using the web printer?',
                        });
                        if (confirmed) {
                            // We want to call the _printWeb when the popup is fully gone
                            // from the screen which happens after the next animation frame.
                            await nextFrame();
                            return await this._printWeb();
                        }
                        return false;
                    }
                } else {
                    return await this._printWeb();
                }
            }

        };

    Registries.Component.extend(ReceiptScreen, PosResReceiptScreen);

    return PosResReceiptScreen;
});
