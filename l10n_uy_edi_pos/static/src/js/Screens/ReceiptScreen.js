odoo.define('l10n_uy_edi_pos.PosResReceiptScreen', function (require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');

    const PosResReceiptScreen = (ReceiptScreen) =>
        class extends ReceiptScreen {
            async _uy_printReceipt(images) {
                return false;
            }
            async printReceipt() {
                var self = this;
                if (this.currentOrder.uy_order_server_id){
                    this.rpc({
                            model: 'pos.order',
                            method: 'get_uy_pdf_invoice',
                            args: [this.currentOrder.uy_order_server_id],
                        }, {
                            timeout: 30000,
                            //shadow: true,
                        })
                        .then(function (data) {
                            if (data.error){
                                alert(data.error);
                            }
                            else if (self.env.pos.config.other_devices && data.images){
                                self.images = data.images;
                                const currentOrder = self.currentOrder;
                                const isPrinted = self._uy_printReceipt(data.images);
                                if (isPrinted) {
                                    currentOrder._printed = true;
                                }
                            }
                            else if (data.url){
                                window.open(data.url, '_blank');
                            }
                            
                        }).catch(function (reason){
                            console.log('Failed to remove orders:', order_server_id);
                        });
                }
                else {
                    return await super.printReceipt();
                }
            }

        };

    Registries.Component.extend(ReceiptScreen, PosResReceiptScreen);

    return PosResReceiptScreen;
});
