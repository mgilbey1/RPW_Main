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
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _check_carrier_quotation(self, force_carrier_id=None):
        # super(SaleOrder, self)._check_carrier_quotation()
        self._remove_delivery_line()
        self.write({'carrier_id': False})
        self.order_line.filtered('is_delivered').write({
            'delivery_carrier_id' : False,
            'delivery_charge' : 0.0,
            'is_delivered': False
        })
        return True


    def _check_carrier_sol_quotation(self, force_carrier_id=None, lines=None):
        self.ensure_one()
        DeliveryCarrier = self.env['delivery.carrier']
        if self.only_services:
            self.write({'carrier_id': None})
            self._remove_delivery_line()
            return True
        else:
            # attempt to use partner's preferred carrier
            if not force_carrier_id and self.partner_shipping_id.property_delivery_carrier_id:
                force_carrier_id = self.partner_shipping_id.property_delivery_carrier_id.id
            carrier = force_carrier_id and DeliveryCarrier.browse(force_carrier_id) or self.carrier_id
            if carrier:
                sol_carrier = DeliveryCarrier.search([('is_sol_carrier','=',True)],limit=1)
                sol_free_config = True if sol_carrier and sol_carrier.sol_free_config == 'y' else None

                res = carrier.sol_carrier_rate_shipment(self, lines=lines, sol_free_config=sol_free_config)

                if sol_carrier:
                    carrier = sol_carrier
                if res.get('success'):
                    shipping_cost = self.get_total_sol_delivery_price()
                    self.set_delivery_line(carrier, shipping_cost)
                    self.delivery_rating_success = True
                    self.delivery_message = res['warning_message']
                else:
                    self.set_delivery_line(carrier, 0.0)
                    self.delivery_rating_success = False
                    self.delivery_message = res['error_message']
        return bool(carrier)

    def get_total_sol_delivery_price(self):
        amount = sum(self.order_line.filtered('is_delivered').mapped('delivery_charge'))
        return amount

    def get_lines_with_or_without_delivery(self):
        """This method used on payment pageself. Return order lines with and without delivery carriers"""
        self.ensure_one()
        order_lines = self.website_order_line
        service_lines = order_lines.filtered(lambda l: l.product_id.type == 'service')
        without_service_lines = order_lines - service_lines
        no_delivery_lines = without_service_lines.filtered(lambda l: len(l.get_delivery_carrier_ids()) == 0)
        delivery_lines = without_service_lines - no_delivery_lines
        return {'no_ol' : no_delivery_lines, 'm_ol': delivery_lines, 's_lines': service_lines}
    

    def _get_delivery_methods(self):
        methods = super(SaleOrder, self)._get_delivery_methods()
        return methods.filtered(lambda m: not m.product_specific)

class SaleOderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("product_id")
    def _compute_available_carrier(self):
        for rec in self:
            carriers = rec.get_delivery_carrier_ids()
            if carriers:
                rec.available_carrier_ids = carriers
            else:
                carriers = self.env['delivery.carrier'].sudo().search([('website_published','=',True),('is_sol_carrier','=',False),('product_specific','=',False)])
                rec.available_carrier_ids = carriers.available_carriers(rec.order_id.partner_shipping_id)

    delivery_carrier_id = fields.Many2one("delivery.carrier", string="Delivery Method")
    delivery_charge = fields.Float("Delivery Price", readonly=True, copy=False)
    available_carrier_ids = fields.Many2many("delivery.carrier", compute='_compute_available_carrier', string="Available Carriers")
    is_delivered = fields.Boolean("Delivered")
    unique_grp_key = fields.Char("Delivery Grouping Key")
    active = fields.Boolean("Active", default=True)

    @api.onchange('product_id')
    def set_deliver_carrier_for_product(self):
        if self.product_id.type == 'service':
            self.delivery_carrier_id = False

    def get_delivery_carrier_ids(self):
        self.ensure_one()
        address = self.order_id.partner_shipping_id
        delivery_carriers = self.product_id.product_tmpl_id.delivery_carrier_ids.filtered('website_published')
        data = delivery_carriers.available_carriers(address)
        return data
