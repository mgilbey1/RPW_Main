# -*- coding: utf-8 -*-
from odoo import models, fields, api
import math

class GoogleModel(models.Model):
    _inherit = 'product.template'
    # define our fields    
    exclude_from_google_export = fields.Boolean("Do NOT include in Google feed", default=False)
    google_id = fields.Integer("Google ID")
    google_gtin = fields.Char("Google GTIN UPC")
    google_category = fields.Integer("Google Category ID number.", default='604')
    ge = 'General Electric (GE)'
    google_brand = fields.Selection([
        ('Affresh', 'Affresh'),
        ('Amana', 'Amana'),
        ('Amana / Goodman', 'Amana / Goodman'),
        ('Amana / Menumaster','Amana / Menumaster'),
        ('Bosch','Bosch'),
        ('Broan','Broan'),
        ('Brown','Brown'),
        ('Carrier','Carrier'),
        ('Chamberlain','Chamberlain'),
        ('Charbroil','Charbroil'),
        ('Coleman','Coleman'),
        ('Core Centric Solutions','Core Centric Solutions'),
        ('Ecodyne','Ecodyne'),
        ('Emerson','Emerson'),
        ('Fisher & Paykel','Fisher & Paykel'),
        ('Frigidaire / Electrolux','Frigidaire / Electrolux'),
        (ge, ge),
        ('Genteq','Genteq'),
        ('Goldstar','Goldstar'),
        ('Greenwald','Greenwald'),
        ('Haier','Haier'),
        ('Harper','Harper'),
        ('Harper Wyman','Harper Wyman'),
        ('Honeywell','Honeywell'),
        ('Horizon','Horizon'),
        ('ICM Controls','ICM Controls'),
        ('Icon','Icon'),
        ('Kenmore','Kenmore'),
        ('KitchenAid','KitchenAid'),
        ('Lennox','Lennox'),
        ('LG','LG'),
        ('Magic Chef','Magic Chef'),
        ('Mastercool','Mastercool'),
        ('Maytag','Maytag'),
        ('MODERN MAID','MODERN MAID'),
        ('MONARCH','MONARCH'),
        ('Nordyne','Nordyne'),
        ('Packard','Packard'),
        ('Panasonic','Panasonic'),
        ('Parts Connect','Parts Connect'),
        ('Peerless Premier','Peerless Premier'),
        ('Proform','Proform'),
        ('Rheem / Ruud','Rheem / Ruud'),
        ('Roper','Roper'),
        ('Rotom','Rotom'),
        ('Samsung','Samsung'),
        ('Sanyo','Sanyo'),
        ('Secop / Nidec','Secop / Nidec'),
        ('Sharp','Sharp'),
        ('Sole','Sole'),
        ('Southeast Specialties','Southeast Specialties'),
        ('Speed Queen','Speed Queen'),
        ('Supco','Supco'),
        ('Tappan','Tappan'),
        ('Titan','Titan'),
        ('Trane','Trane'),
        ('U-LINE','U-LINE'),
        ('Universal Replacement','Universal Replacement'),
        ('Vapco','Vapco'),
        ('Viking','Viking'),
        ('Water Filter Tree','Water Filter Tree'),
        ('WESTINGHOUSE','WESTINGHOUSE'),
        ('Whirlpool','Whirlpool'),
        ('Whirlpool Maytag','Whirlpool Maytag'),
        ('York', 'York')], string="Google Brand")
    
    def generate_gtin(self, product_id):
        # build our check-digit based off of: https://www.gs1.org/services/how-calculate-check-digit-manually
        prefix = "001756"        
        # convert product_id to string
        product_id_string = str(product_id)        
        # add prefix with the product id and pad it with zeros.
        gtin_chunk = prefix + product_id_string.zfill(7)
        # multiply each character by the proper number        
        # Set sum variable
        numbers_sum = 0
        # Set toggle for multiplier (3,1,3,1 ...)
        toggle_multiplier = 3
        for number_from_char in gtin_chunk:
            # convert character to integer
            numbers_sum += int(number_from_char) * toggle_multiplier
            if toggle_multiplier == 3:
                toggle_multiplier = 1
            else:
                toggle_multiplier = 3
        
        # get the next highest tens ceiling
        high_mod = int(math.ceil((numbers_sum + 1) / 10.0)) * 10
        # Calculate check digit
        check_digit = high_mod - numbers_sum
        # put gtin together
        full_gtin = prefix + product_id_string.zfill(7) + str(check_digit)
        return full_gtin
    
    def new_google_id_and_gtin(self):
        if self.google_id == 0:
            new_result_google_id = self.env['product.template'].search([('google_id', '!=', 0)], order='google_id desc', limit=1)
            new_id_num = int(new_result_google_id[0])
            new_google_id = new_id_num + 1
            self.google_id = new_google_id
            self.google_gtin = self.generate_gtin(self.google_id)
        return
    
    @api.onchange('google_id')    
    def update_google_id_and_gtin(self):
        self.env.cr.execute("""select google_id from product_template order by google_id desc nulls last limit 1""")
        update_result_google_id = self.env.cr.fetchone()
        update_id_num = int(update_result_google_id[0])
        update_google_id = update_id_num + 1
        self.google_id = update_google_id
        self.google_gtin = self.generate_gtin(self.google_id)
        return
