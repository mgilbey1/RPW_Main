# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ProductTemplateWebsiteDescription(models.Model):
    _inherit = 'product.template'

    
    web_description = fields.Text('Short Description', help="This description will show up on website as product description.")