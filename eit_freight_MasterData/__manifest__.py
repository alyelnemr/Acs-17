{
    "name": "Freight MasterData",
    "version": "17.0.1.0.1",
    'summary': """
       Freight Forwarding Master Data""",
    'description': """
    This module is provided to handle all kinds of freight operations and integrated with the customer portal on the website to follow the shipments
    """,
    'author': 'EIT-Hub (Expert Information Technology)',
    'website': 'www.eit-hub.com',
    'category': 'Services/Freight',
    "depends": [
        "base", 'mail', 'contacts', 'account', 'product', 'hr_expense', 'purchase', 'sale', 'sale_expense'
    ],
    "data": [
        'security/frieght_secuirity.xml',
        'security/ir.model.access.csv',
        'views/port_cities_view.xml',
        'views/friegt_settings_view.xml',
        'views/service_setting_view.xml',
        'views/configuration_view.xml',
        'views/inherit_res_users_view.xml',
        'views/res_partner_view.xml',
        'views/charge_types_view.xml',
        'views/account_incoterms_view.xml',
        'views/purchase_order_view.xml',
        'views/product_template_view.xml',
        'views/ir_module_view.xml',
        'views/hr_expense_view.xml',
        'views/hr_employee_view.xml',
        'data/demo.xml',
        'data/contaniner_type_demo.xml',
        'data/package.type.csv',
        'data/bill.leading.type.csv',
        'data/shipment.scop.csv',
        'data/service.scope.csv',
        'data/clearence.type.csv',
        'data/tracking.stage.csv',
        'data/activity.type.csv',
        'data/partner.type.csv',
        'data/port.cites.csv',
        'data/res.partner.csv',
        'data/frieght.flights.csv',
        'data/fright.vessels.csv',
        'data/container.data.csv',
        'data/commodity.group.csv',
        'data/commodity.data.csv',
        'data/document.type.csv',
        'data/account.incoterms.csv',
        'data/product.product.csv'
    ],
    "assets": {
        "web.assets_backend": [
            "eit_freight_MasterData/static/src/**/*",
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': True,
    'post_init_hook': 'post_init_hook',
    'license': 'LGPL-3',
}
