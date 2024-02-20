odoo.define('l10n_pe_pos.l10n_pe_pos', function (require) {
"use strict";

var screens = require('point_of_sale.screens');
var rpc = require('web.rpc');
var QWeb = core.qweb;

var _t      = core._t;



screens.PaymentScreenWidget.include({

    order_is_valid: function(force_validation){
        var order = this.pos.get_order();
        if (!order.get_client() && this.pos.config.anonymous_id) {
            var new_client = this.pos.db.get_partner_by_id(this.pos.config.anonymous_id[0]);
            if ( new_client ) {
                order.fiscal_position = _.find(this.pos.fiscal_positions, function (fp) {
                    return fp.id === new_client.property_account_position_id[0];
                });
            } else {
                order.fiscal_position = undefined;
            }
            if (new_client){
                order.set_client(new_client);    
            }
        }
        order.set_to_invoice(true);
        var res = this._super(force_validation);
        return res;
    },
});


});
