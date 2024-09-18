import re

from odoo import api, models


class ProjectTaskChargesReport(models.AbstractModel):
    _name = 'report.eit_freight_operation.report_project_task_op_charges'
    _description = 'Operation Statement Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['project.task'].browse(docids)
        doc_name = ''
        shipping_line = ''
        for line in docs.opt_partners_lines.filtered(lambda x: x.partner_type_id.code == 'SHL'):
            shipping_line = line.partner_id.name
            break
        container = ''
        container_type = ''
        container_qty = len(docs.shipping_container_ids)
        container_type_counts = {}

        # Iterate over the shipping container lines
        for line in docs.shipping_container_ids:
            container_type = line.container_type_id.name

            # Update the count for the container_type in the dictionary
            if container_type in container_type_counts:
                container_type_counts[container_type] += 1
            else:
                container_type_counts[container_type] = 1

        for line in docs.shipping_container_ids:
            container += line.name + ','
            container_type += line.container_type_id.name + ','

        package = ''
        package_qty = len(docs.shipping_package_ids)
        for line in docs.shipping_package_ids:
            package = line.package_type_id.name
            package_qty = line.quantity

        package_type_counts = {}

        # Iterate over the shipping container lines
        for line in docs.shipping_container_ids:
            container_type = line.container_type_id.name

            # Update the count for the container_type in the dictionary
            if container_type in package_type_counts:
                package_type_counts[container_type] += 1
            else:
                package_type_counts[container_type] = 1

        for doc in docs:
            doc_name = doc.name
            new_string = re.sub(r'^.*?\/.*?\/', 'STT/', doc_name) if doc.name != '/' else ''
            doc_name = 'Operation No. ' + doc_name

        return {
            'doc_ids': docids,
            'doc_model': 'project.task',
            'doc_name': doc_name,
            'package': package,
            'package_qty': package_qty,
            'container': container,
            'container_type': container_type,
            'container_qty': container_qty,
            'shipping_line': shipping_line,
            'container_type_counts': container_type_counts,
            'package_type_counts': package_type_counts,
            'docs': docs,
        }
