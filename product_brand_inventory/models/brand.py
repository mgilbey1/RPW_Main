from odoo import models,fields,api


class ProductBrand(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one('product.brand')


class BrandProduct(models.Model):
    _name = 'product.brand'
    _description = 'Manufacturer Name'

    name = fields.Char("Name")
    brand_image = fields.Binary()
    member_ids = fields.One2many('product.template', 'brand_id')
    product_count = fields.Char(string='Product Count', compute='get_count_products', store=True)

    @api.depends('member_ids')
    def get_count_products(self):
        self.product_count = len(self.member_ids)

class BrandReportStock(models.Model):
    _inherit = 'stock.quant'

    brand_id = fields.Many2one(related='product_id.brand_id', string='Manufacturer', store=True, readonly=True)
