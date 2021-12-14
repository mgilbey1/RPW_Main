{
    'name': 'Shipstation Odoo Shipping Connector',
    'version': '14.1.15.12.2021',
    'author': "Vraja Technologies",
    'price': 98,
    'currency': 'EUR',
    'license': 'OPL-1',
    'category': "Website",
    'summary': """""",
    'description': """
    Shipstation Odoo Integration helps you integrate & manage your shipstation account in odoo. manage your Delivery/shipping operations directly from odoo.
    Export Order To Shipstation On Validate Delivery Order.
    Auto Import Tracking Detail From Shipstation to odoo.
    Generate Label in Odoo..
    Also Possible To Import Order From Marketplace/Store.
    We also Provide the ups,dhl,bigcommerce,shiphero,gls,fedex,usps,easyship,stamp.com,dpd,canada post,bpost
""",
    'depends': ['delivery', 'sale', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/product_demo.xml',
        'view/shipstation_odoo_integration_config.xml',
        'view/shipstation_store_view.xml',
        'view/shipstaion_operation_detail.xml',
        'view/shipstation_delivery_carrier.xml',
        'view/shipstation_delivery_carrier_service.xml',
        'view/delivery_carrier.xml',
        'view/shipstation_delivery_carrier_package.xml',
        'view/stock_picking.xml',
        'view/sale_order.xml',
        'view/stock_warehouse.xml',
    ],
    'images': [
        'static/description/odoo_shipstation.png',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# With Shipment import functionality '01.12.2020'
# 14.06.01.2021 fix generate shipment label error messages
# 14.07.01.2021 fix shipstation shipping charge id issue in stock.picking
# 14.19.01.2021 Fix Issue of Service Code not pass proper and add condition for check weight
# 14.21.01.2021 Fix Issue of calculate wrong weight
# 14.10.02.2021 Fix Issue of Multiple Tracking Number
# 14.18.02.2021 Custom tracking link depend on carrier code
# custom changes
# 14.15.12.2021 John beck custom changes
# get rate from volume dimension
# 14.1.15.12.2021 not muliple with quantity
