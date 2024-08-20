from odoo import api, models


class ProjectTaskChargesInvoiceReport(models.AbstractModel):
    _name = 'report.eit_freight_operation.report_project_charges_invoice'
    _description = 'Project Task Charges Invoice Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        doc_name = ''
        shipping_line = ''
        for line in docs.project_task_id.opt_partners_lines.filtered(lambda x: x.partner_type_id.code == 'SHL'):
            shipping_line = line.partner_id.name
            break
        container = ''
        container_type = ''
        container_qty = len(docs.project_task_id.shipping_container_ids)
        for line in docs.project_task_id.shipping_container_ids:
            container += line.name + ','
            container_type += line.container_type_id.name + ','
        package = ''
        package_qty = len(docs.project_task_id.shipping_package_ids)
        for line in docs.project_task_id.shipping_package_ids:
            package = line.package_type_id.name
            package_qty = line.quantity

        for doc in docs:
            doc_name = doc.name
            doc_name = '' if doc.name == '/' else doc_name

        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'doc_name': doc_name,
            'package': package,
            'package_qty': package_qty,
            'container': container,
            'container_type': container_type,
            'container_qty': container_qty,
            'shipping_line': shipping_line,
            'docs': docs,
        }
