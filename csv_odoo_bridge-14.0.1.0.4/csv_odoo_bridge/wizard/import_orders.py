# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
from collections import defaultdict
from io import StringIO,BytesIO
from logging import getLogger
import itertools
import base64
import codecs
import csv
import re

from odoo import api, fields, models, _
from odoo.exceptions import Warning

from ..const import ProductFeedFields, OrderFeedFields
from ..const import ProductFeedFieldsMap,OrderLineFeedFieldsMap,OrderFeedFieldsMap


_logger     = getLogger(__name__)
DecmarkReg  = re.compile('(?<=\d),(?=\d)')
CsvEncoding = [('utf-8', 'UTF-8'), ('utf-16', 'UTF-16')]


class UTF8Recoder:
	"""
	Iterator that reads an encoded stream and reencodes the input to UTF-8
	"""
	def __init__(self, f, encoding):
		self.reader = codecs.getreader(encoding)(f)

	def __iter__(self):
		return self

	def __next__(self):
		return next(self.reader).encode("utf-8").decode()


class UnicodeReader:
	"""
	A CSV reader which will iterate over lines in the CSV file "f",
	which is encoded in the given encoding.
	"""

	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		f = UTF8Recoder(f, encoding)
		self.reader = csv.DictReader(f, dialect=dialect, **kwds)

	def __next__(self):
		row = next(self.reader)
		return row

	def __iter__(self):
		return self


class ImportCSVOrders(models.TransientModel):
	_name    = 'import.csv.orders'
	_inherit = 'import.orders'
	_description = 'Import CSV Wizard'

	csv_file      = fields.Binary('CSV File', required=True)
	csv_encoding  = fields.Selection(CsvEncoding, 'Encoding', default='utf-8')
	csv_quotechar = fields.Char('Quoting Character')
	csv_delimiter = fields.Char('Delimiters Character', default=',', required=True)


	@api.model
	def _csv_get_order_lines(self,item,channel_id,csv_fields,order_vals):
		product_vals = dict()
		line_vals = dict()
		product_feed_fields_map = dict(ProductFeedFieldsMap)
		order_feed_fields_map = dict(OrderFeedFieldsMap)
		order_line_feed_fields_map = dict(OrderLineFeedFieldsMap)
		product_feed_fields=dict(ProductFeedFields)
		for odoo_field,csv_field in csv_fields.items():
			odoo_field= odoo_field
			vals= item.get(csv_field.encode('utf-8').decode())
			if vals :
				if odoo_field in product_feed_fields:
					product_field = product_feed_fields_map.get(odoo_field)
					if product_field:
						vals= product_field in ['list_price','weight','length','width','height'] and DecmarkReg.sub('.',vals) or vals
						product_vals[product_field]=vals
					line_field = order_line_feed_fields_map.get(odoo_field)
					if line_field:
						vals= line_field in ['line_product_uom_qty','line_price_unit'] \
							and DecmarkReg.sub('.',vals) or vals
						line_vals[line_field]=vals
				else:
					order_field = order_feed_fields_map.get(odoo_field)
					if order_field:
						order_vals[order_field]=vals
		product_obj = self.env['product.feed']
		feed = channel_id.match_product_feeds(product_vals.get('store_id'))
		if not feed:
			channel_id._create_feed(product_obj, product_vals)
		else:
			feed.write(product_vals)
		return dict(
			line_vals=line_vals,
			order_vals=order_vals
		)

	@api.model
	def _csv_get_order_vals(self,store_id,order_items,channel_id,csv_fields):
		order_lines = []
		order_vals = dict(store_id=store_id)
		line_type= len(order_items)==1 and 'single' or 'multi'
		order_vals['line_type']=line_type
		for item in order_items:
			res = self._csv_get_order_lines(item,channel_id,csv_fields,order_vals)
			order_vals.update(res.get('order_vals'))
			if line_type=='multi':
				order_lines+=[(0,0,res.get('line_vals'))]
			else:
				order_vals.update(res.get('line_vals'))
		order_vals['line_ids'] =order_lines
		if not order_vals.get('invoice_partner_id'):
			order_vals['invoice_partner_id']=order_vals.get('partner_id')
		if not order_vals.get('invoice_email'):
			order_vals['invoice_email']=order_vals.get('customer_email')
		if not order_vals.get('invoice_name'):
			order_vals['invoice_name']=order_vals.get('customer_name','')
		if not order_vals.get('invoice_last_name'):
			order_vals['invoice_last_name']=order_vals.get('customer_last_name','')
		return order_vals

	@api.model
	def _csv_update_order_feed(self,mapping,store_id,order_items,channel_id,csv_fields):
		vals = self._csv_get_order_vals(store_id,order_items,channel_id,csv_fields)
		mapping.write(dict(line_ids=[(5,0)]))
		mapping.write(vals)
		mapping.write(dict(state='update'))
		return mapping

	@api.model
	def _csv_create_order_feed(self,store_id,order_items,channel_id,csv_fields):
		order_vals = self._csv_get_order_vals(store_id,order_items,channel_id,csv_fields)
		order_obj = self.env['order.feed']
		return self.channel_id._create_feed(order_obj, order_vals)

	@api.model
	def _csv_import_order(self,store_id,order_items,channel_id,csv_fields):
		feed_obj = self.env['order.feed']
		match = channel_id._match_feed(feed_obj, [('store_id', '=', store_id)])
		update=False
		if match :
			self._csv_update_order_feed(match,store_id,order_items,channel_id,csv_fields)
			update=True
		else:
			match= self._csv_create_order_feed(store_id,order_items,channel_id,csv_fields)
		return dict(
			feed_id=match,
			update=update
		)

	@api.model
	def _csv_import_orders(self,items,channel_id,csv_fields):
		create_ids, update_ids=[], []
		for store_id, order_items in items.items():
			import_res = self._csv_import_order(store_id,order_items,channel_id,csv_fields)
			feed_id = import_res.get('feed_id')
			if import_res.get('update'):
				update_ids.append(feed_id)
			else:
				create_ids.append(feed_id)
		return dict(
			create_ids=create_ids,
			update_ids=update_ids,
		)

	def get_csv_order_items(self,csv_fields):
		self.ensure_one()
		reader = []
		message=''
		try:
			file_ref = base64.b64decode(self.csv_file)
			file_input = BytesIO(file_ref)
			params = dict(
				f =file_input,
				encoding = self.csv_encoding,
				delimiter = str(self.csv_delimiter.strip())
			)
			if self.csv_quotechar:
				params['quotechar'] = str(self.csv_quotechar.strip())
			reader = UnicodeReader(**params)
		except Exception as e:
			message +='%s'%(e)
		res = defaultdict(list)
		order_store_id = csv_fields.get('order_store_id').encode('utf-8').decode()
		for line_item in list(reader):
			if order_store_id in line_item:
				res[line_item.get(order_store_id)].append(line_item)
		return dict(
			message=message,
			items=res
		)

	def import_now(self):
		self.ensure_one()
		create_ids,update_ids,map_create_ids,map_update_ids = [],[],[],[]
		message=''
		channel_id = self.channel_id
		csv_fields = dict(
			channel_id.csv_header_mapping_ids.mapped(
				lambda csv_i:(csv_i.odoo_field,csv_i.name)
			)
		)
		csv_res = self.get_csv_order_items(csv_fields)

		message+=csv_res.get('message')
		items = csv_res.get('items')
		if not len(items):
			message+='No item obtain from CSV.'
		else:
			feed_res        = self._csv_import_orders(items,channel_id,csv_fields)
			post_res        = self.post_feed_import_process(channel_id,feed_res)
			create_ids     += post_res.get('create_ids')
			update_ids     += post_res.get('update_ids')
			map_create_ids += post_res.get('map_create_ids')
			map_update_ids += post_res.get('map_update_ids')
			message        += self.env['multi.channel.sale'].get_feed_import_message(
				'order',
				create_ids,
				update_ids,
				map_create_ids,
				map_update_ids,
			)
		return self.env['multi.channel.sale'].display_message(message)
