# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
ProductFeedFieldsMap = [
	('product_store_id','store_id'),
	('product_name','name'),
	('product_default_code','default_code'),
	('product_barcode','barcode'),
	('product_price_unit','list_price'),
	('product_weight','weight'),
	('product_weight_unit','weight_unit'),
	('product_dimensions_unit','dimensions_unit'),
	('product_length','length'),
	('product_width','width'),
	('product_height','height'),
]

OrderLineFeedFieldsMap = [
	('product_store_id','line_product_id'),
	('product_name','line_name'),
	('product_uom_qty','line_product_uom_qty'),
	('product_price_unit','line_price_unit'),
]

OrderFeedFieldsMap = [
	('order_store_id','store_id'),
	('payment_method','payment_method'),
	('carrier_id','carrier_id'),

	('currency','currency'),
	('customer_is_guest','customer_is_guest'),
	('customer_partner_id','partner_id'),
	('customer_email','customer_email'),
	('customer_name','customer_name'),
	('customer_last_name','customer_last_name'),
	('customer_phone','invoice_phone'),
	('customer_mobile','invoice_mobile'),
	('customer_street','invoice_street'),
	('customer_street2','invoice_street2'),
	('customer_city','invoice_city'),
	('customer_zip','invoice_zip'),
	('customer_state_name','invoice_state_name'),
	('customer_state_id','invoice_state_id'),
	('customer_country_id','invoice_country_id'),

	# ('same_shipping_billing','Customer '),
	# ('shipping_partner_id','shipping_partner_id'),
	# ('shipping_name','shipping_name'),
	# ('shipping_last_name','shipping_last_name'),

	# ('shipping_email','shipping_email'),
	# ('shipping_phone','shipping_phone'),
	# ('shipping_mobile','shipping_mobile'),
	# ('shipping_street','shipping_street'),
	# ('shipping_street2','shipping_street2'),
	# ('shipping_city','shipping_city'),
	# ('shipping_zip','shipping_zip'),
	# ('shipping_state_name','shipping_state_name'),
	# ('shipping_state_id','shipping_state_id'),
	# ('shipping_country_id','shipping_country_id'),
	# ('invoice_partner_id','invoice_partner_id'),
	# ('invoice_name','invoice_name'),
	# ('invoice_last_name','invoice_last_name'),

	# ('invoice_email','invoice_email'),
	# ('invoice_phone','invoice_phone'),
	# ('invoice_mobile','invoice_mobile'),
	# ('invoice_street','invoice_street'),
	# ('invoice_street2','invoice_street2'),
	# ('invoice_city','invoice_city'),
	# ('invoice_zip','invoice_zip'),
	# ('invoice_state_name','invoice_state_name'),
	# ('invoice_state_id','invoice_state_id'),
	# ('invoice_country_id','invoice_country_id')
]

ProductFeedFields = [
	('product_store_id','Product Store ID'),
	('product_name','Product Name'),
	('product_default_code','Product Default Code'),
	('product_barcode','Product Barcode'),
	('product_uom_qty','Product Qty'),
	('product_price_unit','Product Price'),

	('product_weight','Product Weight'),
	('product_weight_unit','Product Weight Unit'),
	('product_dimensions_unit','Product Dimensions Unit'),
	('product_length','Product Length'),
	('product_width','Product Width'),
	('product_height','Product Height'),
]

OrderFeedFields = [
	('order_store_id','Order Store ID'),
	('payment_method','Payment Method Name'),
	('carrier_id','Delivery Method Name'),

	('currency','Currency Code'),
	('customer_is_guest','Customer Is Guest'),
	('customer_partner_id','Customer Store ID'),
	('customer_email','Customer Email'),
	('customer_name','Customer Name'),
	('customer_last_name','Customer Last Name'),

	('customer_phone','Customer  Phone'),
	('customer_mobile','Customer  Mobile'),
	('customer_street','Customer  Street'),
	('customer_street2','Customer  Street2'),
	('customer_city','Customer  City'),
	('customer_zip','Customer  Zip'),
	('customer_state_name','Customer  State Name'),
	('customer_state_id','Customer  State Code'),
	('customer_country_id','Customer  Country Code'),


	# ('same_shipping_billing','Customer '),
	# ('shipping_partner_id','Shipping Partner ID'),
	# ('shipping_name','Shipping Partner Name'),
	# ('shipping_last_name','Shipping Partner Last Name'),

	# ('shipping_email','Shipping Partner Email '),
	# ('shipping_phone','Shipping Partner Phone'),
	# ('shipping_mobile','Shipping Partner Mobile'),
	# ('shipping_street','Shipping Partner Street'),
	# ('shipping_street2','Shipping Partner Street2'),
	# ('shipping_city','Shipping Partner City'),
	# ('shipping_zip','Shipping Partner Zip'),
	# ('shipping_state_name','Shipping Partner State Name'),
	# ('shipping_state_id','Shipping Partner State Code'),
	# ('shipping_country_id','Shipping Partner Country Code'),
	# ('invoice_partner_id','Invoice Partner ID'),
	# ('invoice_name','Invoice Partner Name'),
	# ('customer_last_name','Invoice Partner Last Name'),

	# ('invoice_email','Invoice Partner Email'),
	# ('invoice_phone','Invoice Partner Phone'),
	# ('invoice_mobile','Invoice Partner Mobile'),
	# ('invoice_street','Invoice Partner Street'),
	# ('invoice_street2','Invoice Partner Street2'),
	# ('invoice_city','Invoice Partner City'),
	# ('invoice_zip','Invoice Partner Zip'),
	# ('invoice_state_name','Invoice Partner State Name'),
	# ('invoice_state_id','Invoice Partner State Code'),
	# ('invoice_country_id','Invoice Partner Country Code'),
]
