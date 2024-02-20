odoo.define('l10n_uy_edi_pos.PosResPaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { isConnectionError } = require('point_of_sale.utils');

    const PosResPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            async validateOrder(isForceValidate) {
                //var order = this.env.pos.get_order()
                this.currentOrder.set_to_invoice(true);
                if (!this.currentOrder.get_partner() && this.env.pos.config.uy_anonymous_id){
                    var new_client = this.env.pos.db.get_partner_by_id(this.env.pos.config.uy_anonymous_id[0]);
                    if (new_client){
                        this.currentOrder.set_partner(new_client);
                    }
                }
                if (!this.currentOrder.get_partner()){
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Missing Customer'),
                        body: this.env._t("You must have a client assigned"),
                    });
                    return;
                }
                var client = this.currentOrder.get_partner();

                if (client.uy_doc_type){
                    if (!client.vat){
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Client rut number'),
                            body: this.env._t("You must enter number rut"),
                        });
                        return;
                    }
                    if (!client.street){
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Client Address'),
                            body: this.env._t("You must enter an address"),
                        });
                        return;
                    }
                    if (!client.city){
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Client City'),
                            body: this.env._t("You must enter an city"),
                        });
                        return;
                    }
                    if (!client.state_id){
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Client State'),
                            body: this.env._t("You must enter an state"),
                        });
                        return;
                    }
                        
                }
                var qty_error = "";
                var price_error = "";
                for (var i = 0; i < this.currentOrder.orderlines.length; i++) {
                    if (this.currentOrder.orderlines[i].quantity==0.0){
                        qty_error+=this.currentOrder.orderlines.models[i].get_product().display_name + "\n";
                    }
                    if (this.currentOrder.orderlines[i].price==0.0){
                        price_error+=this.currentOrder.orderlines[i].get_product().display_name + "\n";
                    }
                }
                /*this.currentOrder.orderlines.each(_.bind( function(item) {
                    if (item.qty==0.0){
                        qty_error+=item.get_product().name + "<br />";
                    }
                }, this));  */
                
                if (qty_error!=""){
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('The product quantity must be greater than zero'),
                        body: qty_error,
                    });
                    return;
                }
                if (price_error!=""){
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('The product price must be greater than zero'),
                        body: qty_error,
                    });
                    return;
                }
                return await super.validateOrder(isForceValidate);
            }

            async _finalizeValidation() {
                if ((this.currentOrder.is_paid_with_cash() || this.currentOrder.get_change()) && this.env.pos.config.iface_cashdrawer) {
                    this.env.proxy.printer.open_cashbox();
                }

                this.currentOrder.initialize_validation_date();
                this.currentOrder.finalized = true;

                let syncOrderResult, hasError;

                try {
                    // 1. Save order to server.
                    syncOrderResult = await this.env.pos.push_single_order(this.currentOrder);

                    // 2. Invoice.
                    if (this.currentOrder.is_to_invoice()) {
                        if (syncOrderResult.length) {
                            /*await this.env.legacyActionManager.do_action('account.account_invoices', {
                                additional_context: {
                                    active_ids: [syncOrderResult[0].account_move],
                                },
                            });*/
                            this.currentOrder.uy_order_server_id = syncOrderResult[0].id
                        } else {
                            throw { code: 401, message: 'Backend Invoice', data: { order: this.currentOrder } };
                        }
                    }

                    // 3. Post process.
                    if (syncOrderResult.length && this.currentOrder.wait_for_push_order()) {
                        const postPushResult = await this._postPushOrderResolve(
                            this.currentOrder,
                            syncOrderResult.map((res) => res.id)
                        );
                        if (!postPushResult) {
                            this.showPopup('ErrorPopup', {
                                title: this.env._t('Error: no internet connection.'),
                                body: this.env._t('Some, if not all, post-processing after syncing order failed.'),
                            });
                        }
                    }
                } catch (error) {
                    if (error.code == 700 || error.code == 701)
                        this.error = true;

                    if ('code' in error) {
                        // We started putting `code` in the rejected object for invoicing error.
                        // We can continue with that convention such that when the error has `code`,
                        // then it is an error when invoicing. Besides, _handlePushOrderError was
                        // introduce to handle invoicing error logic.
                        await this._handlePushOrderError(error);
                    } else {
                        // We don't block for connection error. But we rethrow for any other errors.
                        if (isConnectionError(error)) {
                            this.showPopup('OfflineErrorPopup', {
                                title: this.env._t('Connection Error'),
                                body: this.env._t('Order is not synced. Check your internet connection'),
                            });
                        } else {
                            throw error;
                        }
                    }
                } finally {
                    // Always show the next screen regardless of error since pos has to
                    // continue working even offline.
                    this.showScreen(this.nextScreen);
                    // Remove the order from the local storage so that when we refresh the page, the order
                    // won't be there
                    this.env.pos.db.remove_unpaid_order(this.currentOrder);

                    // Ask the user to sync the remaining unsynced orders.
                    if (!hasError && syncOrderResult && this.env.pos.db.get_orders().length) {
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            title: this.env._t('Remaining unsynced orders'),
                            body: this.env._t(
                                'There are unsynced orders. Do you want to sync these orders?'
                            ),
                        });
                        if (confirmed) {
                            // NOTE: Not yet sure if this should be awaited or not.
                            // If awaited, some operations like changing screen
                            // might not work.
                            this.env.pos.push_orders();
                        }
                    }
                }
            }
        };

    Registries.Component.extend(PaymentScreen, PosResPaymentScreen);

    return PosResPaymentScreen;
});
