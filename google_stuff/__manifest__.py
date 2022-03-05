# -*- coding: utf-8 -*-
{
    'name': "Google Tab",

    'summary': """
        Adds a google specific export stuff to products""",

    'description': """
        This module adds a google specific stuff to products.
    """,

    'author': "John Beck",
    'website': "https://devbeck.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Website',
    'version': '1.026.220305b',

    # any module necessary for this one to work correctly
    'depends': ['delivery', 'sale', 'base', 'stock'],

    # always loaded
    'data': [
        'views/product_google_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
