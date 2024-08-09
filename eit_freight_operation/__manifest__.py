{
    "name": "Freight Operations",
    "version": "17.0.1.0.6",
    'summary': """
        Freight Forwarding Operations""",
    'description': """
    This module is provided to handle all kinds of freight operations and integrated with the customer portal on the website to follow the shipments 
    """,
    'website': 'http://www.eit-hub.com',
    'author': "EIT-Hub (Expert Information Technology)  www.eit-hub.com",
    'category': 'Services/Freight',
    "depends": ['base', 'project', 'eit_freight_MasterData', 'hr_expense', 'documents', 'sale_project',
                'documents_project'],
    "data": [
        'security/ir.model.access.csv',
        'security/project_security.xml',
        'data/project_task_type.xml',
        'views/project_project_views.xml',
        'views/project_task_type_view.xml',
        'views/project_task_view.xml',
        'wizard/origin_route_view.xml',
        'wizard/trasit_route_view.xml',
        'wizard/destination_route_view.xml',
        'wizard/project_task_closing_wizard_views.xml',
    ],
    'demo': [
        'data/project_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
