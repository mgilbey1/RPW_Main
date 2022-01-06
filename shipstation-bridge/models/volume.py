# -*- coding: utf-8 -*-
#################################################################################
# Author        : John Beck (<https://devbeck.com>)
# Copyright(c)  : 2021 to Present John Beck
# All Rights Reserved
#################################################################################

from odoo import api, models, fields

class ProductDimensions(models.Model):
    _inherit = 'product.template'
    # declare our form fields
    product_length = fields.Char(string="Length")
    product_width = fields.Char(string="Width")
    product_height = fields.Char(string="Height")

    #product_uom = field.Selection(string='Product Unit of Measure', selection=selection=[('imperial','Imperial'), ('metric', 'Metric')])

    
    @api.onchange('product_length', 'product_width', 'product_height')
    def _onchange_lengh_width_height(self):
        self.volume = float(self.product_length if self.product_length else 0) * float(self.product_width if self.product_width else 0) * float(self.product_height if self.product_height else 0)
