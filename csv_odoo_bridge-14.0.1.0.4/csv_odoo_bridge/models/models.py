# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from logging import getLogger
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from ..const import ProductFeedFields, OrderFeedFields


_logger = getLogger(__name__)


class CSVHeaderMappings(models.Model):
	_name = 'csv.header.mappings'
	_description = 'Header Mappings'

	name       = fields.Char('Header', required=True)
	channel_id = fields.Many2one('multi.channel.sale', 'Channel')

	odoo_field = fields.Selection(
		selection=ProductFeedFields+OrderFeedFields,
		string='Field',
		required=True,
	)

	_sql_constraints = [
		(
			'value_channel_odoo_field_uniq',
			'unique (channel_id,odoo_field)',
			'This odoo field  already mapped !'
		)
	]


class MultiChannelSale(models.Model):
	_inherit = 'multi.channel.sale'

	csv_header_mapping_ids = fields.One2many(
		comodel_name='csv.header.mappings',
		inverse_name='channel_id',
		string='Header Mappings',
	)


	@api.constrains('csv_header_mapping_ids')
	def _check_csv_header_mapping_ids(self):
		for rec in self:
			mapping_ids = rec.csv_header_mapping_ids.filtered(
				lambda mp: mp.odoo_field in [
					'product_store_id',
					'order_store_id',
					'customer_partner_id'
				]
			)
			if len(mapping_ids)!=3 and self.channel=='csv':
				raise ValidationError('Product Store ID ,Order Store ID and Customer Store ID must be mapped.')

	def test_csv_connection(self):
		self.state = 'validate'

	@api.model
	def get_channel(self):
		result = super(MultiChannelSale, self).get_channel()
		result.append(('csv', 'CSV'))
		return result

	@api.model
	def get_info_urls(self):
		urls = super(MultiChannelSale,self).get_info_urls()
		urls.update(
			csv = {
				'blog' : 'https://webkul.com/blog/odoo-import-orders-csv/',
				'store': 'https://store.webkul.com/Odoo-Import-Orders-From-CSV.html',
			},
		)
		return urls

	def action_import_csv(self):
		pass
