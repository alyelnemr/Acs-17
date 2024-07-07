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

    'category': 'Services/Freight',
    'version': '17.0',
    'license': 'LGPL-3',
    'application': False,

    'assets': {
        'web.assets_frontend': [
            '/eit_freight_request_quote/static/src/js/main.js'
        ]
    },
    'depends': ['base', 'website', 'eit_freight_MasterData', 'eit_freight_sales', 'sale_crm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/request_quote.xml',
        'views/crm_lead_views.xml',
    ],
}
