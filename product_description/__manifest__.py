# -*- coding: utf-8 -*-
{
    'name': "Product Description",

    'summary': """
        Adds a product description field to the ecommerce tab with HTML support.""",

    'description': """
        This module adds a product description field to the ecommerce tab with HTML support, that displays on the native template for individual products.
    """,

    'author': "John Beck",
    'website': "https://devbeck.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_templates_views.xml',
        'views/product_product_views.xml',
        'views/templates.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
