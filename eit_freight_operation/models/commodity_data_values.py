from odoo import models, fields, api, _


class CommodityDtaValues(models.Model):
    _name = "commodity.data.values"

    commodity_data_id = fields.Many2one('commodity.data', string="Commodity")
    code = fields.Char(string="Hs Code", related="commodity_data_id.code")
    tax = fields.Integer(string="Import Tax", related="commodity_data_id.tax")
    vat = fields.Integer(string="Vat", related="commodity_data_id.vat")
    type = fields.Selection([('dry', 'Dry'), ('reefer', 'Reefer'), ('imo', 'IMO')], string="Equip",
                            related="commodity_data_id.type")
    tag_id = fields.Many2many('frieght.tags', string="Tags", related="commodity_data_id.tag_id_1")
    export_approval = fields.Many2many('commodity.data.approval.export'
                                       , string="Export Approvals", )
    export_custom = fields.Many2many('commodity.data.custom.export'
                                     , string="Export Req")
    task_commodity = fields.Many2one('project.task')
    commo_data_valus = fields.Many2one('origin.services')
    service_scope_id = fields.Many2one('service.scope', string="Service", related="commo_data_valus.service_scope_id")
    clearence_type_id = fields.Many2one('clearence.type', string="Direction",
                                        related="commo_data_valus.clearence_type_id")
    import_approval = fields.Many2many('commodity.data.approval.import'
                                       , string="Import Approvals")
    import_custom = fields.Many2many('commodity.data.custom.import'
                                    , string="Import Req")
    acid = fields.Integer(string="ACID",related="commo_data_valus.acid")

    @api.onchange('commodity_data_id')
    def onchange_commodity_data_id(self):
        ep_a = []
        ep_c = []
        im_a = []
        im_c = []
        export_app = self.commodity_data_id.export_approval
        for line in export_app:
            ep_a.append(line.id)
        self.export_approval = ep_a
        export_cut = self.commodity_data_id.export_custom
        for lineep in export_cut:
            ep_a.append(lineep.id)
        import_ap = self.commodity_data_id.import_approval
        for ima in import_ap:
            im_a.append(ima.id)
        import_cu = self.commodity_data_id.import_custom
        for imc in import_cu:
            im_c.append(imc.id)
        self.export_custom = ep_c
        self.import_approval = im_a
        self.import_custom = im_c


class CleraenceStages(models.Model):
    _name = "clearence.stages"

    stage_id = fields.Many2one('tracking.stage', string="Stage", domain="[('docs_type', '=', 'custom_doc')]")
    start_date = fields.Date(string="Start date")
    end_date = fields.Date(string="End date")
    description = fields.Text(string="Description")
    stages_service_id = fields.Many2one('origin.services')
