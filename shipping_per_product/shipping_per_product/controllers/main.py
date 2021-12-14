# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import http, _
from odoo.tools import float_round
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)

class ProductShipping(http.Controller):

    def _format_amount(self, amount, currency):
        fmt = "%.{0}f".format(currency.decimal_places)
        lang = request.env['res.lang']._lang_get(request.env.context.get('lang') or 'en_US')
        return lang.format(fmt, currency.round(amount), grouping=True, monetary=True)\
            .replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'-\N{ZERO WIDTH NO-BREAK SPACE}')

    def sol_update_website_sale_delivery_return(self, order, carrier_id, lines):
        Monetary = request.env['ir.qweb.field.monetary']
        if order:
            currency = order.currency_id
            sol_delivery_amount = sum(lines.mapped('delivery_charge'))
            # sol_delivery_amount = float_round(sol_delivery_amount, 2)
            new_total_delivery_amount = order.get_total_sol_delivery_price()
            # new_total_delivery_amount = float_round(new_total_delivery_amount, 2)
            return {
                'status': order.delivery_rating_success,
                'error_message': order.delivery_message,
                'carrier_id': carrier_id,
                'is_free_delivery': not bool(order.amount_delivery),
                'sol_delivery_amount': self._format_amount(sol_delivery_amount,currency),
                'new_amount_delivery': self._format_amount(new_total_delivery_amount,currency),
                'new_amount_untaxed': self._format_amount(order.amount_untaxed,currency),
                'new_amount_tax': self._format_amount(order.amount_tax,currency),
                'new_amount_total': self._format_amount(order.amount_total,currency),
            }
        return {}

    @http.route(['/shop/sol/update_carrier'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_shop_sol_carrier(self, **post):
        order = request.website.sale_get_order()
        carrier_id = int(post['carrier_id'])
        order_lines = post.get('order_lines')
        order_lines = request.env["sale.order.line"].sudo().browse(order_lines)
        if order:
            order._check_carrier_sol_quotation(force_carrier_id=carrier_id, lines=order_lines)
        return self.sol_update_website_sale_delivery_return(order, carrier_id, order_lines)
