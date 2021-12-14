from odoo import fields,models,api,_
import base64
from datetime import datetime
from requests import request
import time
import binascii
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"
    
    shipstation_warehouse_id = fields.Many2one('shipstation.warehouse.detail',string="Shipstation Warehouse")
    