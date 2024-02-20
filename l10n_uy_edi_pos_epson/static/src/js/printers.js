
odoo.define('l10n_pe_pos_cpe.Printer', function (require) {
"use strict";

var core = require('web.core');
//var { PrinterMixin, PrintResult, PrintResultGenerator } = require('point_of_sale.Printer');
var EpsonPrinter = require('pos_epson_printer.Printer');

var QWeb = core.qweb;
var _t = core._t;

/*class EpsonPrintResultGenerator extends PrintResultGenerator {
    constructor(address) {
        super();
    }
}*/



EpsonPrinter.include({
    /*htmlToImg: function (receipt) {
        var canvas = document.createElement("canvas");
        var image = new Image();
        image.onload = function() {
            var ctx = canvas.getContext("2d");
            ctx.drawImage(image, 0, 0);
        };
        image.src = "data:image/jpeg;base64,"+img;
        return canvas;
    },*/
    /**
     * Create the raster data from a canvas
     *
     * @override
     */
    
    async print_pdf_receipt(images){
        var receipt = '<div class="pos-receipt" style="width:'+images[0].width+'px; height:'+images[0].height+'px" ><img width="'+images[0].width+'" height="'+images[0].height+'" src="data:image/png;base64,'+images[0].image+'"></div>';
        return await this.print_receipt(receipt);
        /*if (receipt) {
            this.receipt_queue.push(receipt);
        }
        let image, sendPrintResult;
        while (this.receipt_queue.length > 0) {
            receipt = this.receipt_queue.shift();
            image = await this.htmlToImg(receipt);
            try {
                sendPrintResult = await this.send_printing_job(image);
            } catch (_error) {
                // Error in communicating to the IoT box.
                this.receipt_queue.length = 0;
                return this.printResultGenerator.IoTActionError();
            }
            // rpc call is okay but printing failed because
            // IoT box can't find a printer.
            if (!sendPrintResult || sendPrintResult.result === false) {
                this.receipt_queue.length = 0;
                return this.printResultGenerator.IoTResultError(sendPrintResult.printerErrorCode);
            }
        }
        return this.printResultGenerator.Successful();*/
    },

    /*process_canvas(canvas) {
        var canvas2 = document.createElement("canvas");
        var image = new Image();
        canvas2.width = 512;
        canvas2.height = 589;
        image.onload = function() {
            var ctx = canvas2.getContext("2d");
            ctx.drawImage(image, 0, 0);
        };
        image.src = "data:image/jpeg;base64,"+img;
        var rasterData = this._canvasToRaster(canvas2);
        var encodedData = this._encodeRaster(rasterData);
        //var encodedData = pdfExample;
        return QWeb.render('ePOSPrintImage', {
            image: encodedData,
            width: canvas.width,
            height: canvas.height,
        });
    },*/

    /**
     * @override
     */
    /*async send_printing_job(img) {

        const res = await $.ajax({
            url: this.address,
            method: 'POST',
            data: img,
        });
        const response = $(res).find('response');
        return {"result": response.attr('success') === 'true', "printerErrorCode": response.attr('code')};
    },*/
});

return EpsonPrinter;

});
