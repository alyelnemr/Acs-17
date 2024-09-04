from odoo import models, fields


class OperationRouteDocument(models.Model):
    _name = 'operation.route.document'
    _description = 'Document'
    _rec_name = 'document_name'

    document_type_id = fields.Many2one(comodel_name='document.type', string="Document Type", required=True, domain=[('type', '=', 'odoc')])
    document_name = fields.Char(string="Document Name", required=False)
    reviewed = fields.Boolean(string="Reviewed")
    received_in = fields.Date(string="Received In", default=fields.Date.today())
    operation_route_id = fields.Many2one(comodel_name='operation.route', string='Operation Route', ondelete='cascade')
