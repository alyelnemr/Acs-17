/** @odoo-module **/

import {
StateSelectionField,
stateSelectionField,
} from "@web/views/fields/state_selection/state_selection_field";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { escape } from "@web/core/utils/strings";
import { markup } from "@odoo/owl";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(StateSelectionField.prototype, {
    setup() {
        super.setup();
        this.dialog = useService("dialog");
    },

    async updateRecord(value) {
        if (value === "1_done") {
            return new Promise((resolve) => {
                const message = "Are you sure you want to set this Operation as ";
                this.dialog.add(ConfirmationDialog, {
                    body: markup(`<div>${escape(message)}<span class="text-danger"><b>Closed</b></span> ?</div>`),
                    confirm: () => super.updateRecord(value),
                    cancel: () => {},
                });
            });
        } else {
            return super.updateRecord(value);
        }
    }
});