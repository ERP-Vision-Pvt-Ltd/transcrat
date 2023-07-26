# -*- coding: utf-8 -*-
{
    'name': "Transcrate Shipox Odoo Connector",

    'summary': """
        Transcrate Odoo ConnectorTranscrate Integration with ODOO V-16)
        """,

    'description': """
       Transcrate Odoo Connector(Transcrate Integration with ODOO V-16)
    """,

    'author': "ERP VISION",
    'website': "http://www.erpvision.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '16.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','account','payment','sale_stock'],

    # always loaded
    'data': [
        'data/schedule.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/shipbox_instance_views.xml',
        'views/shipbox_city_views.xml',
        'views/shipbox_country_views.xml',
        'views/shipbox_neighborhoods_views.xml',
        'views/shipbox_service_type_views.xml',
        'views/res_partner_views.xml',
        'views/stock_picking_views.xml',
        'views/res_company_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
    'price':'350.0',
    'currency': 'USD',
    'images': ['static/description/images/shipox.gif'],
    'maintainer':'ERP VISION',
    'installable': True,
    'application': True,

}
