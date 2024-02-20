odoo.define('l10n_uy_edi_pos.PartnerDetailsEdit', function (require) {
    "use strict";

var PartnerDetailsEdit = require('point_of_sale.PartnerDetailsEdit');
const Registries = require('point_of_sale.Registries');

const PartnerDetailsEditUy = PartnerDetailsEdit => class extends PartnerDetailsEdit {
    setup(){
        super.setup();
        this.intFields.push('city_id');
    }
}
Registries.Component.extend(PartnerDetailsEdit, PartnerDetailsEditUy);

});
