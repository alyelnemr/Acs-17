/** @odoo-module **/

import {patch} from "@web/core/utils/patch";
import {ListController} from "@web/views/list/list_controller";
import {useService} from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
const cogMenuRegistry = registry.category("cogMenu");

patch(ListController.prototype, {
    /**
     * @override
     */
    async setup() {
        super.setup();
        this.orm = useService("orm");
        const currentModel = this.props.resModel;
        const modelList = ['port.cites', 'res.country','res.country.group','transport.type',
        'package.type','container.type','container.data','bill.leading.type','shipment.scop',
        'freight.vessels','freight.airplane','product.product','service.scope','clearence.type',
        'tracking.stage','activity.type','account.incoterms','commodity.group','commodity.data','partner.type',
        'document.type','frieght.tags'];
        this.modelInList = modelList.includes(currentModel);

        const currentUser = await this.orm.call(
            "res.users",
            "get_is_hide_archive_and_applied_models"
        );
        this.is_hide_archive_user = currentUser.is_hide_archive_user;
        this.is_hide_archive_manager = currentUser.is_hide_archive_manager;
        this.is_hide_archive_admin = currentUser.is_hide_archive_admin;

        if (this.is_hide_archive_user && !this.is_hide_archive_manager) {
            cogMenuRegistry.remove("export-all-menu");
            cogMenuRegistry.remove("spreadsheet-cog-menu");
        }

        if (this.is_hide_archive_manager && !this.is_hide_archive_admin) {
            cogMenuRegistry.remove("export-all-menu");
            cogMenuRegistry.remove("spreadsheet-cog-menu");
        }
    },

    get actionMenuItems() {
        const actionMenus = super.actionMenuItems;
        const { action } = actionMenus;

        let filteredAction = action;

//        if (this.modelInList) {
//            filteredAction = filteredAction.filter((item) => item.key === "archive" && item.key === "unarchive");
//        }

        if (this.is_hide_archive_user && !this.is_hide_archive_manager) {
            filteredAction = filteredAction.filter((item) =>
                item.key !== "archive" &&
                item.key !== "unarchive" &&
                item.key !== "export" &&
                item.key !== "duplicate"
            );
        }

        if (this.is_hide_archive_manager && !this.is_hide_archive_admin) {
        if (this.modelInList) {
         filteredAction = filteredAction.filter((item) =>
                item.key !== "export" &&
                item.key !== "duplicate"
            );
        }
        }

        actionMenus.action = filteredAction;
        return actionMenus;
    },
});
