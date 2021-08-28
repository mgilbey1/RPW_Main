# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import api,fields,models


class ImportOperation(models.TransientModel):
	_inherit = 'import.operation'

	def csv_get_filter(self):
		return {}

	def import_with_filter(self,**kw):
		if self.channel == 'csv' and self.object == 'sale.order':
			action = self.env.ref('csv_odoo_bridge.action_import_csv_orders').read()[0]
			action.update(context={'default_channel_id': self.channel_id.id})
			return action
		else:
			return super().import_with_filter(**kw)
