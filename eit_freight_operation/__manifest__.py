{
    "name": "Custom Project",
    "version": "17.0.1.0.1",
    'summary': """
        Project Customosation""",
    'description': """
    This module is provided to handle all kinds of freight operations and integrated with the customer portal on the website to follow the shipments 
    """,
    'author': "EIT-Hub (Expert Information Technology)  www.eit-hub.com",
    'category': 'Services/Freight',
    "depends": ['base', 'project', 'eit_freight_MasterData', 'hr_expense'],
    "data": [
        'security/ir.model.access.csv',
        'data/project_task_type.xml',
        'views/project_task_type_view.xml',
        'views/project_task_view.xml',
        'wizard/origin_route_view.xml',
        'wizard/trasit_route_view.xml',
        'wizard/destination_route_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
