# -*- coding: utf-8 -*-
{
    'name': "Freight Workflow",

    'summary': """
        Freight Forwarding Sales Pricing Workflow
        """,

    'description': """
        Freight Forwarding Sales Pricing Workflow.
    """,

    'author': "EIT-Hub (Expert Information Technology)",
    'website': 'www.eit-hub.com',

    'category': 'Services/Freight',
    'version': '17.0',
    'license': 'LGPL-3',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': [
        'base', 'crm', 'sale_management',
        'account', 'eit_freight_MasterData', 'eit_freight_sales', 'eit_freight_operation', 'eit_freight_pricing',
        'sale_crm', 'web', 'website'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/pricing_crm_security.xml',
        'wizard/confirm_message_wizard.xml',
        'views/pricing_views.xml',
        'views/project_task_view.xml',
        'views/crm_lead_view.xml',
    ],
}
