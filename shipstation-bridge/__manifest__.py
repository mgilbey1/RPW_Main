{
    'name': 'Shipstation Bridge',
    'version': '01.5.020922',
    'author': "John Beck",
    'price': '400',
    'currency': 'USD',
    'license': 'OPL-1',
    'category': "Website",
    'summary': """
        Shipstation and Odoo bridge with dimensional shipping, and shipping method rules.
    """,
    'description': """
        Shipstation and Odoo bridge is a newer experience in integrating Shipstation with Odoo. 
        Often missing in other modules, Shipstation Bridge includes the following features: Integrated sales, 
        shipping, and labeling, rates and shipping use both real product dimensions or dimensional weight when getting shipping
        prices, and it allows you to better compuete multiple items per box - by reducing the number of "per item" shipping 
        calculations.
    """,
    'depends': ['delivery', 'sale', 'base', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/product_demo.xml',
        'views/shipstation_odoo_integration_config.xml',
        'views/shipstation_store_view.xml',
        'views/shipstaion_operation_detail.xml',
        'views/shipstation_delivery_carrier.xml',
        'views/shipstation_delivery_carrier_service.xml',
        'views/delivery_carrier.xml',
        'views/shipstation_delivery_carrier_package.xml',
        'views/stock_picking.xml',
        'views/sale_order.xml',
        'views/stock_warehouse.xml',
        'views/volume_view.xml',
    ],
    'images': [
        'static/description/odoo_shipstation.png',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
