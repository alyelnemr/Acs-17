from odoo import models, fields, api


class MainCarriageWizard(models.TransientModel):
    _name = 'main.carriage.wizard'
    _description = 'Main Carriage Wizard'

    # Define fields as Char and readonly
    port_id = fields.Char(string='Port', readonly=True)
    planned_date_from = fields.Char(string='Planned Date From', readonly=True)
    planned_date_to = fields.Char(string='Planned Date To', readonly=True)
    vessel_id = fields.Char(string='Vessel', readonly=True)
    flight_no = fields.Char(string='Flight Number', readonly=True)
    truck_no = fields.Char(string='Truck Number', readonly=True)
    port_id_pod = fields.Char(string='Port of Discharge', readonly=True)
    transit_time = fields.Char(string='Transit Time', readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super(MainCarriageWizard, self).default_get(fields_list)
        # Fetch data from project.task (adjust as necessary)
        task_id = self.env.context.get('active_id')
        if task_id:
            task = self.env['project.task'].browse(task_id)
            # Assuming the task has the corresponding fields and using 'name' instead of 'id'
            res.update({
                'port_id': task.port_id.name if task.port_id else '',
                'planned_date_from': task.planned_date_from if task.planned_date_from else '',
                'planned_date_to': task.planned_date_to if task.planned_date_to else '',
                'vessel_id': task.vessel_id.name if task.vessel_id else '',
                'flight_no': task.flight_no or '',
                'truck_no': task.truck_no or '',
                'port_id_pod': task.port_id_pod.name if task.port_id_pod else '',
                'transit_time': str(task.transit_time) if task.transit_time else '',
            })
        return res
