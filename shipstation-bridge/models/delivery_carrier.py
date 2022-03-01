import base64
import json
import logging
import time
from datetime import datetime
from requests import request
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    shipstation_carrier_id = fields.Many2one('shipstation.delivery.carrier', string='Shipstation Carrier')
    shipstation_delivery_carrier_service_id = fields.Many2one('shipstation.delivery.carrier.service',
                                                              string='Shipstation Delivey Carrier Service')
    delivery_type = fields.Selection(selection_add=[('shipstation', 'Shipstation')], ondelete={'shipstation': 'set default'})
    delivery_package_id = fields.Many2one('shipstation.delivery.package', string='Shipstation Package Code')
    weight_uom = fields.Selection([('pounds', 'pounds'), ('ounces', 'ounces'), ('grams', 'grams')], default="pounds",
                                  string='Weight UOM')
    shipstation_dimensions = fields.Selection([('inches', 'inches'), ('centimeters', 'centimeters')], default="inches",
                                              string='Shipstation dimensions')
    confirmation = fields.Selection(
        [('none', 'None'), ('delivery', 'Delivery'), ('signature', 'Signature'), ('adult_signature', 'adult_signature'),
         ('direct_signature', 'direct_signature')], default="none",
        string='Shipstation Confirmation')
    store_id = fields.Many2one('shipstation.store', "Store")

    def get_total_weight(self, weight=1):
        pound_for_kg = 2.20462
        ounce_for_kg = 35.274
        grams_for_kg = 1000
        ounce_for_lb = 16
        grams_for_lb = 453.592
        uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        if self.weight_uom == "pounds" and uom_id.name in ['lb','lbs']:
            return round(weight, 3)
        elif self.weight_uom == "pounds" and uom_id.name == 'kg':
            return round(weight * pound_for_kg, 3)
        elif self.weight_uom == "ounces" and uom_id.name in ['lb','lbs']:
            return round(weight * ounce_for_lb, 3)
        elif self.weight_uom == "ounces" and uom_id.name == 'kg':
            return round(weight * ounce_for_kg, 3)
        elif self.weight_uom == "grams" and uom_id.name == 'kg':
            return round(weight * grams_for_kg, 3)
        else:
            return round(weight * grams_for_lb, 3)

    def check_order_data(self, order):
        lines_without_weight = order.order_line.filtered(
            lambda line_item: not line_item.product_id.type in ['service','digital'] and not line_item.product_id.weight and not line_item.is_delivery)
        for order_line in lines_without_weight:
            return _("Please define weight in product : \n %s") % order_line.product_id.name
        receiver_address = order.partner_shipping_id
        sender_address = order.warehouse_id.partner_id
        if not receiver_address.zip or not receiver_address.country_id or not receiver_address.city:
            return _("Please define proper receiver address.")
        if not sender_address.zip or not sender_address.country_id or not sender_address.city:
            return _("Please define proper receiver address.")

        return False

    def api_calling_function(self, url_data, body):
        configuration = self.env['shipstation.odoo.configuration'].search([], limit=1)
        if not configuration:
            raise ValidationError("Configuration Not Done.")
        url = configuration.making_shipstation_url(url_data)
        api_secret = configuration.api_secret
        api_key = configuration.api_key
        data = "%s:%s" % (api_key, api_secret)
        encode_data = base64.b64encode(data.encode("utf-8"))
        authrization_data = "Basic %s" % (encode_data.decode("utf-8"))
        headers = {"Authorization": authrization_data,
                   "Content-Type": "application/json"}
        data = json.dumps(body)
        _logger.info("Request Data: %s" % (data))
        try:
            response_body = request(method='POST', url=url, data=data, headers=headers)
        except Exception as e:
            raise ValidationError(e)
        return response_body
       
    def shipstation_rate_shipment(self, order):
        try: 
            # shipstation_charge_id = self.env['shipstation.shipping.charge'].search([('sale_order_id', '=', order and order.id),('shipstation_provider','=',self.shipstation_carrier_id.code)], order='shipping_cost')
            shipstation_charge_id = self.env['shipstation.shipping.charge'].search([('sale_order_id', '=', order and order.id)])
            shipstation_charge_id.sudo().unlink()
        except Exception:
            self._cr.rollback()  # error, rollback everything atomically
        finally:
            self._cr.commit()
        weight_split = False
        ground_ship_only = False
        checked_order_data = self.check_order_data(order)
        shipping_charge_obj = self.env['shipstation.shipping.charge']
        if checked_order_data:
            return {'success': False, 'price': 0.0, 'error_message': checked_order_data, 'warning_message': False}
        receiver_address = order.partner_shipping_id
        sender_address = order.warehouse_id.partner_id
        weight = sum([(line.product_id.weight * line.product_uom_qty) for line in order.order_line if not line.is_delivery])
        # total_weight = float(self.get_total_weight(weight))
        total_weight = weight
        total_shipment_volume = 0.0
        for line_item in order.order_line:
            line_item_failed = False
            product_rec = self.env['product.product'].browse(line_item.product_id.id)
            product_tmpl_id = product_rec.product_tmpl_id
            product_tmpl_rec = self.env['product.template'].browse(product_tmpl_id.id)
            if product_tmpl_rec.type != "service":
                rec_item_length = product_tmpl_rec.product_length
                rec_item_width = product_tmpl_rec.product_width
                rec_item_height = product_tmpl_rec.product_height
                ground_ship_only_check = bool(product_tmpl_rec.product_ground_ship_only)
                if ground_ship_only_check == True:
                    ground_ship_only = True
                item_length = float(rec_item_length)
                item_width = float(rec_item_width)
                item_height = float(rec_item_height)
                # Check if package is bigger than can be shipped
                max_package_length = self.delivery_package_id.length
                max_package_width = self.delivery_package_id.width
                max_package_height = self.delivery_package_id.height
                if item_length <= 0.0 or item_width <= 0.0 or item_height <= 0.0:
                    item_length = 0.125
                    item_width = 0.125
                    item_height = 0.125
                # Compute the volume of our predefined shipping package (e.g. One Rate Pak)
                max_package_volume = max_package_length * max_package_width * max_package_height
                # Compute the volume item
                item_package_volume = item_length * item_width * item_height
                # Check if the line item's size is too big for our selected package size.
                if item_package_volume > max_package_volume:
                    # Our item is too big to ship with this method, fail and exit
                    line_item_failed = True
                    return {'success': False, 'price': 0.0, 'error_message': "Not Available",'warning_message': False}
                # add this line item's volume to our total shipment's volume
                total_shipment_volume += (item_package_volume * line_item.product_uom_qty)
        if total_shipment_volume > max_package_volume:
            number_of_packages = total_shipment_volume / max_package_volume
        else:
            number_of_packages = 1
        if self.shipstation_delivery_carrier_service_id.service_code == "fedex_home_delivery" and total_weight > 250:
            return {'success': False, 'price': 0.0, 'error_message': "Please contact us for a quote.",'warning_message': False}
        # Check for ground ship only
        if ground_ship_only == True:
            if self.shipstation_delivery_carrier_service_id.service_code != "fedex_home_delivery":
                return {'success': False, 'price': 0.0, 'error_message': "Not Available",'warning_message': False}
            else:
                # continue processing but make sure we have a weight of a lb or more.
                if total_weight < 2: 
                    total_weight = 1.5
                # Check if the weight of our order is over 70lbs
                if total_weight > 70:
                    weight_split = True
        # Check for need to split order into multiple packages if not, continue with regular process
        if max_package_volume > total_shipment_volume:
            package_split = False
            if total_weight < 70:
                weight_split = False
            else:
                weight_split = True 
            # Single Box  
            cube_root = total_shipment_volume ** (1./3)
            line_width = round(cube_root,3)
            line_length = round(cube_root,3)
            line_height = round(cube_root,3)
            total_weight = round(total_weight, 2)
            # Setup special rule for Smart Economy
            # Make sure that the package isn't over-weight
            if self.shipstation_delivery_carrier_service_id.service_code == "smartmail_parcels_expedited":
                if total_weight <= 1:
                    total_shipment_volume = max_package_volume
                    line_width = max_package_width
                    line_length = max_package_length
                    line_height = max_package_height
                    total_weight = round(total_weight, 2)
                else:
                    return {'success': False, 'price': 0.0, 'error_message': "Not Available",'warning_message': False}
            if self.shipstation_delivery_carrier_service_id.service_code == "fedex_smartpost_parcel_select" and total_shipment_volume < 750:
                cube_root = 750 ** (1./3)
                line_width = round(cube_root,3)
                line_length = round(cube_root,3)
                line_height = round(cube_root,3)
                total_weight = round(total_weight, 2)
            dict_rate = {
                "carrierCode": "%s" % (self.shipstation_carrier_id and self.shipstation_carrier_id.code),
                "packageCode": "%s" % (self.delivery_package_id and self.delivery_package_id.package_code),
                "fromPostalCode": "%s" % (sender_address.zip),
                "toState": "%s" % (receiver_address.state_id and receiver_address.state_id.code),
                "toCountry": "%s" % (receiver_address.country_id and receiver_address.country_id.code),
                "toPostalCode": "%s" % (receiver_address.zip),
                "toCity": receiver_address.city,
                "weight": {
                    "value": total_weight,
                    "units": self.weight_uom or "pounds"
                },
                "dimensions": {
                    "units": self.shipstation_dimensions or "inches",
                    "length": line_length,
                    "width": line_width,
                    "height": line_height,
                },
                "confirmation": self.confirmation or "none",
                # "residential": True
                "residential": self.shipstation_delivery_carrier_service_id and self.shipstation_delivery_carrier_service_id.residential_address
            }
        elif line_item_failed == False:
            # package split required - we are going to use the maximum package's size (the one currently set) for our initial cost.
            package_split = True
            per_full_package_weight = round(total_weight, 2) / round(number_of_packages, 2)
            per_weight = round(per_full_package_weight, 2)
            # Check weight limits and add packages and change max size if needed.
            if per_weight > 70:
                weight_split = True
                per_weight_box_splitting = round(total_weight, 2) / 70  # = 2.792857148571427
                # Increase the number of packages so that they fit the weight limit.
                if number_of_packages < per_weight_box_splitting:
                    number_of_packages = round(per_weight_box_splitting, 2)  # redundant but it keeps us safe.
                # Calculate new max box size
                new_package_volume = total_shipment_volume / number_of_packages  # = 
                new_package_volume = round(new_package_volume, 2)
                new_box_dimension = new_package_volume ** (1./3)  # = 
                max_package_length = round(new_box_dimension, 2)
                max_package_width = round(new_box_dimension, 2)
                max_package_height = round(new_box_dimension, 2)
                new_weight = total_weight / number_of_packages
                total_weight = round(new_weight, 2)
                
            dict_rate = {
                "carrierCode": "%s" % (self.shipstation_carrier_id and self.shipstation_carrier_id.code),
                "packageCode": "%s" % (self.delivery_package_id and self.delivery_package_id.package_code),
                "fromPostalCode": "%s" % (sender_address.zip),
                "toState": "%s" % (receiver_address.state_id and receiver_address.state_id.code),
                "toCountry": "%s" % (receiver_address.country_id and receiver_address.country_id.code),
                "toPostalCode": "%s" % (receiver_address.zip),
                "toCity": receiver_address.city,
                "weight": {
                    "value": total_weight,
                    "units": self.weight_uom or "pounds"
                },
                "dimensions": {
                    "units": self.shipstation_dimensions or "inches",
                    "length": max_package_length or 1,
                    "width": max_package_width or 1,
                    "height": max_package_height or 1,
                },
                "confirmation": self.confirmation or "none",
                # "residential": True
                "residential": self.shipstation_delivery_carrier_service_id and self.shipstation_delivery_carrier_service_id.residential_address
            }           
        # USE API to get rates.
        try:
            response_data = self.api_calling_function("/shipments/getrates", dict_rate)
            if response_data.status_code == 200:
                responses = response_data.json()
                _logger.info("Response Data: %s" % (responses))
                if responses:
                    # Do a check to make sure we actually have the shipping method available
                    ship_method_present = False
                    for ship_method_available in responses:
                        ship_method = ship_method_available.get('serviceCode')
                        if ship_method == self.shipstation_delivery_carrier_service_id.service_code:
                            ship_method_present = True
                    # End of check
                    # Kick it back as an error if not there                    
                    if ship_method_present == False:
                        return {'success': False, 'price': 0.0, 'error_message': "Not Available", 'warning_message': False} 
                    # Proceed with regular rate retrieval                   
                    for response in responses:
                        shipping_charge_obj.sudo().create(
                            {'shipstation_provider': self.shipstation_carrier_id.code, 'shipstation_service_code': response.get('serviceCode'),
                             'shipstation_service_name': response.get('serviceName'),
                             'shipping_cost': response.get('shipmentCost', 0.0),
                             'other_cost': response.get('otherCost', 0.0),
                             'sale_order_id': order and order.id})
                        self._cr.commit()
                    shipstation_charge_id = self.env['shipstation.shipping.charge'].search([('sale_order_id', '=', order and order.id),('shipstation_service_code','=',self.shipstation_delivery_carrier_service_id.service_code)],limit=1)                
                    if not shipstation_charge_id:
                        shipstation_charge_id = self.env['shipstation.shipping.charge'].search([('sale_order_id', '=', order and order.id),('shipstation_provider','=',self.shipstation_carrier_id.code)], order='shipping_cost', limit=1)
                        order.shipstation_shipping_charge_id = shipstation_charge_id and shipstation_charge_id.id
                    if weight_split:
                        weight_split = False
                        pre_rounded_rate_amount = (shipstation_charge_id.shipping_cost + shipstation_charge_id.other_cost) * round(number_of_packages, 2)
                        rate_amount = round(pre_rounded_rate_amount, 2)
                        return {'success': True, 'price': rate_amount or 0.0,'error_message': False, 'warning_message': False} 
                    # Our Package Splitting magic - We are using volumes here.
                    if package_split:
                        max_package_ship_cost = shipstation_charge_id.shipping_cost
                        float(max_package_ship_cost)
                        # Setup special rules
                        # If package has more than 2 boxes, deny fedex_2day
                        if self.shipstation_delivery_carrier_service_id.service_code == "fedex_2day":
                            if number_of_packages > 2:
                                return {'success': False, 'price': 0.0, 'error_message': "Not Available", 'warning_message': False}
                        
                        # deny package splitting for smartmail packages
                        if self.shipstation_delivery_carrier_service_id.service_code == "smartmail_parcels_expedited":
                            return {'success': False, 'price': 0.0, 'error_message': "Not Available", 'warning_message': False}
                        
                        # Smallest Package Computations
                        # get the smallest (or last) package and figure out it's dimensional info
                        full_packages = int(number_of_packages)
                        full_packages_volume = full_packages * round(max_package_volume, 2)
                        remaining_volume = round(total_shipment_volume, 2) - round(full_packages_volume, 2)
                        if remaining_volume > 0:  # make sure we have a remainder
                            # Get weight per volume
                            weight_per_volume = total_weight / total_shipment_volume
                            full_packages_weight = weight_per_volume * full_packages_volume
                            remaining_weight = total_weight - full_packages_weight
                            rounded_remaining_weight = round(remaining_weight)                                    
                            # compute package dimensions
                            remaining_package_wlh = remaining_volume ** (1./3)
                            rounded_remaining_package_wlh = round(remaining_package_wlh, 2)
                            # New dict    
                            remaining_package_dict = {
                                "carrierCode": "%s" % (self.shipstation_carrier_id and self.shipstation_carrier_id.code),
                                "packageCode": "%s" % (self.delivery_package_id and self.delivery_package_id.package_code),
                                "fromPostalCode": "%s" % (sender_address.zip),
                                "toState": "%s" % (receiver_address.state_id and receiver_address.state_id.code),
                                "toCountry": "%s" % (receiver_address.country_id and receiver_address.country_id.code),
                                "toPostalCode": "%s" % (receiver_address.zip),
                                "toCity": receiver_address.city,
                                "weight": {
                                    "value": rounded_remaining_weight,
                                    "units": self.weight_uom or "pounds",
                                },
                                "dimensions": {
                                    "units": self.shipstation_dimensions or "inches",
                                    "length": rounded_remaining_package_wlh or max_package_length,
                                    "width": rounded_remaining_package_wlh or max_package_width,
                                    "height": rounded_remaining_package_wlh or max_package_height
                                },
                                "confirmation": self.confirmation or "none",
                                "residential": self.shipstation_delivery_carrier_service_id and self.shipstation_delivery_carrier_service_id.residential_address
                            }
                            remainder_response_data = self.api_calling_function("/shipments/getrates", remaining_package_dict)
                            if remainder_response_data.status_code == 200:
                                remainder_json_data = remainder_response_data.json()
                                remainder_ship_method = self.shipstation_delivery_carrier_service_id.service_code
                                remainder_package_rate = 0.0
                                for chunk in remainder_json_data:
                                    if chunk.get('serviceCode') == remainder_ship_method:
                                        remainder_shipment_cost = chunk.get('shipmentCost')
                                        remainder_shipment_other_cost = chunk.get('otherCost')
                                        remainder_package_rate = remainder_shipment_cost + remainder_shipment_other_cost
                                rate_amount = ((max_package_ship_cost + shipstation_charge_id.other_cost) * full_packages) + remainder_package_rate
                            else:
                                rate_amount = (max_package_ship_cost + shipstation_charge_id.other_cost) * number_of_packages
                    else:
                        package_split = False
                        weight_split = False
                    pre_rounded_rate_amount = shipstation_charge_id.shipping_cost + shipstation_charge_id.other_cost
                    rate_amount = round(pre_rounded_rate_amount, 2)
                    return {'success': True, 'price': rate_amount or 0.0,'error_message': False, 'warning_message': False}    
                else:
                    package_split = False
                    weight_split = False
                    return {'success': False, 'price': 0.0, 'error_message': "Not Available", 'warning_message': False}
            elif response_data.status_code == 500:
                error_message_details = ""
                if response_data.json():
                    error_response_data = response_data.json()
                    error_message_details = error_response_data.get('ExceptionMessage')
                return {'success': False, 'price': 0.0,
                        'error_message': "%s" % (error_message_details),
                        'warning_message': False}
            else:
                error_code = "%s" % (response_data.status_code)
                error_message = response_data.reason
                error_detail = {'error': error_code + " - " + error_message + " - "}
                return {'success': False, 'price': 0.0, 'error_message': error_detail,
                        'warning_message': False}
        except Exception as e:
            return {'success': False, 'price': 0.0, 'error_message': e,
                    'warning_message': False}

    def generate_label_from_shipstation(self, picking, package_id=False, weight=False):
        package_length = package_id.packaging_id.packaging_length if package_id and package_id.packaging_id else self.delivery_package_id.length
        shipstation_shipping_charge_id = picking.sale_id.shipstation_shipping_charge_id
        shipstation_service_code = shipstation_shipping_charge_id.shipstation_service_code if picking.sale_id.shipstation_shipping_charge_id else picking.carrier_id.shipstation_delivery_carrier_service_id.service_code
        custom_package_id = package_id and package_id.packaging_id or self.delivery_package_id
        total_weight = self.get_total_weight(weight)
        request_data = {
            "orderId": "%s" % (picking.shipstation_order_id),
            "carrierCode": "%s" % (self.shipstation_carrier_id and self.shipstation_carrier_id.code),
            "serviceCode": "%s" % (shipstation_service_code),
            "packageCode": "%s" % ((package_id.packaging_id.shipper_package_code if package_id and package_id.packaging_id and package_id.packaging_id else self.delivery_package_id.package_code) or ""),
            "confirmation": self.confirmation or "none",
            "shipDate": "%s" % (time.strftime("%Y-%m-%d")),
            "testLabel": True if not self.prod_environment else False,
            "weight": {
                "value": total_weight,
                "units": self.weight_uom or "pounds",
            },
            "dimensions": {
                "units": self.shipstation_dimensions or "inches",
                "length": package_length or 0.0,
                "width": custom_package_id.width or 0.0,
                "height": custom_package_id.height or 0.0
            },
        }
        return request_data

    def get_order_item_details(self, picking):
        res = []
        count = 0
        for move_line in picking.move_lines:
            total_weight = self.get_total_weight(move_line.product_id.weight)
            count = count + 1
            item_dict = {
                "lineItemKey": "%s" % (count),
                "sku": "%s" % (move_line.product_id and move_line.product_id.default_code),
                "name": "%s" % (move_line.sale_line_id and move_line.sale_line_id.name),
                "weight": {
                    "value": "%s" % (total_weight),
                    "units": self.weight_uom or "pounds"
                },
                "quantity": int(move_line.product_uom_qty),
                "unitPrice": "%s" % (move_line.sale_line_id.price_unit if move_line.sale_line_id.price_unit else move_line.product_id and move_line.product_id.lst_price),
                "productId": "%s" % (move_line.product_id and move_line.product_id.id)}
            res.append(item_dict)
        return res

    def create_or_update_order(self, picking):
        if not self.store_id:
            raise ValidationError("Store Not Configured!")
        picking_receiver_id = picking.partner_id
        # picking_sender_id = picking.picking_type_id.warehouse_id.partner_id
        total_value = picking.sale_id.amount_total if picking.sale_id.amount_total else sum([(line.product_uom_qty * line.product_id.list_price) for line in picking.move_lines]) or 0.0
        warehouse_id = picking.picking_type_id.warehouse_id.shipstation_warehouse_id and picking.picking_type_id.warehouse_id.shipstation_warehouse_id.warehouse_id
        weight = picking.shipping_weight

        total_weight = self.get_total_weight(weight)

        date_order = picking.scheduled_date
        if date_order:
            order_date_formate = datetime.strptime(str(date_order), "%Y-%m-%d %H:%M:%S")
            order_date = order_date_formate.strftime('%Y-%m-%dT%H:%M:%S')
            request_data = {
                "orderNumber": "%s" % (picking.origin if picking.origin else picking.name),
                "orderDate": "%s" % (order_date),
                "shipByDate": "%s" % (order_date),
                "orderStatus": "awaiting_shipment",
                "customerUsername": "%s" % (picking_receiver_id.name),
                "customerEmail": "%s" % (picking_receiver_id.email or ""),
                "billTo": {
                    "name": "%s" % (picking_receiver_id.name),
                    "company": "",
                    "street1": "%s" % (picking_receiver_id.street or ""),
                    "street2": "%s" % (picking_receiver_id.street2 or ""),
                    "city": "%s" % (picking_receiver_id.city or ""),
                    "state": "%s" % (picking_receiver_id.state_id and picking_receiver_id.state_id.code or ""),
                    "postalCode": "%s" % (picking_receiver_id.zip or ""),
                    "country": "%s" % (picking_receiver_id.country_id and picking_receiver_id.country_id.code or ""),
                    "phone": "%s" % (picking_receiver_id.phone or ""),
                    "residential": self.shipstation_delivery_carrier_service_id and self.shipstation_delivery_carrier_service_id.residential_address
                },
                "shipTo": {
                    "name": "%s" % (picking_receiver_id.name),
                    "company": "",
                    "street1": "%s" % (picking_receiver_id.street or ""),
                    "street2": "%s" % (picking_receiver_id.street2 or ""),
                    "city": "%s" % (picking_receiver_id.city or ""),
                    "state": "%s" % (picking_receiver_id.state_id and picking_receiver_id.state_id.code or ""),
                    "postalCode": "%s" % (picking_receiver_id.zip or ""),
                    "country": "%s" % (picking_receiver_id.country_id and picking_receiver_id.country_id.code or ""),
                    "phone": "%s" % (picking_receiver_id.phone or ""),
                    "residential": self.shipstation_delivery_carrier_service_id and self.shipstation_delivery_carrier_service_id.residential_address
                },
                "items": self.get_order_item_details(picking),
                "amountPaid": total_value,
                "shippingAmount": sum(picking.sale_id.mapped('order_line').filtered(lambda line:line.is_delivery == True).mapped('price_subtotal')) or 0.0,
                "carrierCode": "%s" % (self.shipstation_carrier_id and self.shipstation_carrier_id.code),
                "serviceCode": "%s" % (
                        self.shipstation_delivery_carrier_service_id and self.shipstation_delivery_carrier_service_id.service_code),
                "packageCode": "%s" % (self.delivery_package_id and self.delivery_package_id.package_code or ""),
                "confirmation": self.confirmation or "none",
                "internalNotes":picking.note or '',
                "shipDate": "%s" % (order_date),
                "weight": {
                    "value": total_weight,
                    "units": "%s" % (self.weight_uom)
                },
                "dimensions": {
                    "units": "%s" % (self.shipstation_dimensions),
                    "length": self.delivery_package_id and self.delivery_package_id.length or 0.0,
                    "width": self.delivery_package_id and self.delivery_package_id.width or 0.0,
                    "height": self.delivery_package_id and self.delivery_package_id.height or 0.0,
                },
                "insuranceOptions": {
                    "provider": "%s" % (self.shipstation_carrier_id and self.shipstation_carrier_id.code),
                    "insureShipment": False,
                    "insuredValue": 0
                },
                "advancedOptions": {
                    # TODO We need to send when import wh from shipstation "warehouseId": ,
                    "storeId": self.store_id and self.store_id.store_id or ""
                },
                "tagIds": [picking.id]
            }
            if warehouse_id:
                request_data.get('advancedOptions').update({"warehouseId": warehouse_id})
        return request_data

    @api.model
    def shipstation_send_shipping(self, pickings):
        for picking in pickings:
            if any(move.product_id.weight <= 0.0 for move in picking.move_lines):
                raise ValidationError("Need to set Product Weight.")
            if not picking.shipstation_order_id:
                body = self.create_or_update_order(picking)
                try:
                    response_data = self.api_calling_function("/orders/createorder", body)
                    if response_data.status_code == 200:
                        responses = response_data.json()
                        _logger.info("Response Data: %s" % (responses))
                        order_id = responses.get('orderId')
                        order_key = responses.get('orderKey')
                        order_number = responses.get('orderNumber')
                        if order_id:
                            picking.shipstation_order_id = order_id
                            picking.shipstation_order_key = order_key
                            picking.shipstation_sale_order_number = order_number
                            picking.carrier_price = responses.get('shipmentCost', 0.0)
                            if not (picking and picking.sale_id and picking.sale_id.shipstation_order_number):
                                picking.sale_id.shipstation_order_number = order_number
                                picking.sale_id.shipstation_order_id = order_id
                                picking.sale_id.is_exported_to_shipstation = True
                                picking.sale_id.shipstation_store_id = picking.carrier_id and picking.carrier_id.store_id.id
                        return [{'exact_price': 0.0, 'tracking_number': ''}]
                    else:
                        error_code = "%s" % (response_data.status_code)
                        error_message = response_data.reason
                        error_detail = {'error': error_code + " - " + error_message + " - "}
                        if response_data.json():
                            error_detail = {'error': error_code + " - " + error_message + " - %s" % (response_data.json())}
                        raise ValidationError(error_detail)
                except Exception as e:
                    raise ValidationError(e)

    def shipstation_cancel_shipment(self, picking):
        shipment_id = picking.shipstation_shipment_id
        if not shipment_id:
            raise ValidationError("Shipstation Shipment Id Not Available!")
        req_data = {"shipmentId": '{}'.format(shipment_id)}
        try:
            response_data = self.api_calling_function("/shipments/voidlabel", req_data)
            if response_data.status_code == 200:
                responses = response_data.json()
                _logger.info("Response Data: %s" % (responses))
                approved = responses.get('approved')
                if approved:
                    picking.message_post(body=_('Shipment Cancelled In Shipstation %s' % (shipment_id)))
            else:
                error_code = "%s" % (response_data.status_code)
                error_message = response_data.reason
                error_detail = {'error': error_code + " - " + error_message + " - "}
                if response_data.json():
                    error_detail = {'error': error_code + " - " + error_message + " - %s" % (response_data.json())}
                raise ValidationError(error_detail)
        except Exception as e:
            raise ValidationError(e)
        return True

    def shipstation_get_tracking_link(self, pickings):
        res = ""
        for picking in pickings:
            link = "%s" % (
                        picking.carrier_id and picking.carrier_id.shipstation_carrier_id and picking.carrier_id and picking.carrier_id.shipstation_carrier_id.provider_tracking_link)
            if not link:
                raise ValidationError("Provider Link Is not available")
            if len(pickings.carrier_tracking_ref.split(',')) > 1:
                if self.shipstation_carrier_id and self.shipstation_carrier_id.code in ["ups", "UPS", "ups_walleted", "UPS_WALLETED"]:
                    res = '%s %s' % (link, pickings.carrier_tracking_ref.replace(",", "%20"))
                elif self.shipstation_carrier_id and self.shipstation_carrier_id.code in ["stamps_com", "STAMPS_COM"]:
                    res = '%s %s' % (link, pickings.carrier_tracking_ref.replace(",", "%2C"))
                else:
                    res = '%s %s' % (link, pickings.carrier_tracking_ref.replace(",","&"))
            else:
                res = '%s %s' % (link, pickings.carrier_tracking_ref)

        return res
