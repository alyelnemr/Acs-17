/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.Select2ToInit = publicWidget.Widget.extend({
        selector: '#to_port_cities',
        start: function () {
            this._super.apply(this, arguments);
            this.$el.select2({
                placeholder: "Select Port/Cities...",
                allowClear: true
            });
        },
    });

publicWidget.registry.Select2FromInit = publicWidget.Widget.extend({
        selector: '#from_port_cities',
        start: function () {
            this._super.apply(this, arguments);
            this.$el.select2({
                placeholder: "Select Port/Cities...",
                allowClear: true
            });
//            this.$el.on('select2:select select2:unselect', function (e) {
//                // Manually trigger change event to ensure form validation
//                $(this).trigger('change');
//            });
//            this.$el.closest('form').on('submit', function (e) {
//                debugger;
//                if (this.getElementsByClassName('select_from_port_cities')) {
//                    var select_from_port_cities = this.getElementsByClassName('select_from_port_cities')[0];
//                    if(select_from_port_cities.value == null || select_from_port_cities.value == "") {
//                        select_from_port_cities.addClass('select2-required');
//                        e.preventDefault();
//                        e.stopPropagation();
//                    } else {
//                        self.$el.next('.select2').find('.select2-selection').removeClass('select2-required');
//                    }
//                }
//
//            });
        },
    });