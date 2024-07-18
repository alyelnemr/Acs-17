# -*- coding: utf-8 -*-
{
    'name': "EIT Freight Request quote",

    'summary': """
        EIT Freight Request a quote form
        """,

    'description': """
        The request-a-quote module allows visitors to send shipping request rates with seamless CRM integration.
    """,

    'author': "EIT-Hub (Expert Information Technology)",
    'website': 'www.eit-hub.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list

    'category': 'Services/Freight',
    'version': '17.0',
    'license': 'LGPL-3',
    'application': False,

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'sale_management', 'account', 'eit_freight_MasterData', 'sale_crm', 'web', 'website'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/crm_lead_view.xml',
        'views/sale_order_view.xml',
        'views/request_quote.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/eit_freight_sales/static/src/js/main.js',
            '/eit_freight_sales/static/src/img/quote-bg.png',
            '/eit_freight_sales/static/src/js/select2_init.js',
        ],
        'web.assets_backend': [
            '/eit_freight_sales/static/lib/select2.min.css',
            '/eit_freight_sales/static/lib/select2.min.js',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
