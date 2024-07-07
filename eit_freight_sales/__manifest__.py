# -*- coding: utf-8 -*-
{
    'name': "Sales Freight",

    'summary': """
        Freight Forwarding Sales Process""",

    'description': """
        Freight Forwarding Sales Process
    """,

    'author': "EIT-Hub (Expert Information Technology)",
    'website': 'www.eit-hub.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Services/Freight',
    'version': '17.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'sale_management', 'account', 'eit_freight_MasterData', 'sale_crm', 'website'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/crm_lead_view.xml',
        'views/request_quote.xml',
        'views/sale_order_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': False
}
