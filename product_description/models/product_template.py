# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ProductTemplateWebsiteDescription(models.Model):
    _inherit = 'product.template'

    
    web_description = fields.Text('Website Description', help="This description will show up on website as product description.")
    do_not_include_in_google_feed = fields.Boolean("Do NOT include in Google feed", default=False)
    google_id = fields.Char(string="Google ID")
    google_tin = fields.Char(string="Google TIN")