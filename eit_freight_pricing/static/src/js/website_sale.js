/** @odoo-module **/

import { WebsiteSale } from '@website_sale/js/website_sale';
import publicWidget from '@web/legacy/js/public/public_widget';

publicWidget.registry.WebsiteSale.include({
    /**
     * Override the _onClickAddCartJSON function to add custom behavior.
     * @param {Event} ev
     */
    _onClickAdd: function (ev) {
        // Call the original function to retain the existing behavior
        this._super.apply(this, arguments);

        // Add your custom functionality here
        console.log('Custom functionality after adding product to cart');

        // Example: Trigger a custom event or show a custom message
//        alert('Product added to cart!');

        // You can also add any other logic, like analytics tracking, custom UI updates, etc.
    },
});
