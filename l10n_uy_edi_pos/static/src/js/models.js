odoo.define('l10n_uy_edi_pos.models', function (require) {
    "use strict";

var { PosGlobalState, Order } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');


const PosEdiUyPosGlobalState = (PosGlobalState) => class PosEdiUyPosGlobalState extends PosGlobalState {
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.cities = loadedData['res.city'];
        this.uy_doc_types = [['2','RUT'],['3','C.I.'],['4','Otros'],['5','Pasaporte'],['6','DNI']];
        console.log(this.cities);
        //this.employee_by_id = loadedData['employee_by_id'];

    }
}
Registries.Model.extend(PosGlobalState, PosEdiUyPosGlobalState);


const PosEdiOrder = (Order) => class PosEdiOrder extends Order {
    constructor(obj, options) {
        super(...arguments);
        this.uy_order_server_id = false;
    }
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        if (json.uy_order_server_id) {
            this.uy_order_server_id = json.uy_order_server_id;
        }
    }
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.uy_order_server_id = this.uy_order_server_id;
        return json;
    }
}
Registries.Model.extend(Order, PosEdiOrder);

});
