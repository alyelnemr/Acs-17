# -*- coding: utf-8 -*-
{
    'name': "Pricing",

    'summary': """Freight Forwarding Pricing""",

    'description': """The pricing module is for publishing shipping rates on the website with integration to get a Quote or Make a booking online""",

    'author': "EIT-Hub (Expert Information Technology) ",
    'website': "www.eit-hub.com",

    'category': 'Services/Freight',
    'version': '17.2',
    'depends': ['base', 'purchase', 'eit_freight_MasterData', 'account', 'base_setup', 'product', 'base_setup',
                'mail', 'website_sale', 'hr_expense'],

    'data': [
        'security/pricing_security.xml',
        'security/ir.model.access.csv',
        'security/stage_pricing_data.xml',
        'views/product_template_view.xml',
        'views/pricing_view.xml',
        'views/request_price_view.xml',
        'views/purchase_order_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'wizard/request_price_vendor_view.xml',

    ],

    'installable': True,
    'application': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
