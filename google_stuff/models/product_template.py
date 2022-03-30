# -*- coding: utf-8 -*-
from odoo import models, fields
import math

class GoogleModel(models.Model):
    _inherit = 'product.template'
    # define our fields    
    exclude_from_google_export = fields.Boolean("Do NOT include in Google feed", default=False)
    google_id = fields.Integer("Google ID")
    google_gtin = fields.Char("Google GTIN UPC")
    google_category = fields.Integer("Google Category ID number.", default='604')
    save_field = fields.Char("Record State", default="<font color='#FF0000'>&lt;&lt;&lt;<strong> NOT SAVED! </strong>&gt;&gt;&gt;</font>")
    ge = 'General Electric (GE)'
    google_brand = fields.Selection([
        ('affresh','Affresh'),
        ('amana','Amana'),
        ('amana_goodman','Amana / Goodman'),
        ('amana_menumaster','Amana / Menumaster'),
        ('ami','AMI'),
        ('aftermarket','Aftermarket'),
        ('bosch','Bosch'),
        ('bosch_therm', 'Bosch/Thermador'),
        ('broan','Broan'),
        ('brown','Brown'),
        ('carrier','Carrier'),
        ('chamberlain','Chamberlain'),
        ('charbroil','Charbroil'),
        ('chromalox','Chromalox'),
        ('coleman','Coleman'),
        ('core_centric_solutions','Core Centric Solutions'),
        ('ecodyne','Ecodyne'),
        ('emerson','Emerson'),
        ('fisher_paykel','Fisher & Paykel'),
        ('frigidaire_electrolux','c / Electrolux'),
        ('ge', ge),
        ('genteq','Genteq'),
        ('goldstar','Goldstar'),
        ('greenwald','Greenwald'),
        ('haier','Haier'),
        ('harper','Harper'),
        ('harper wyman','Harper Wyman'),
        ('honeywell','Honeywell'),
        ('horizon','Horizon'),
        ('icm_controls','ICM Controls'),
        ('icon','Icon'),
        ('johnson','Johnson Health Tech'),
        ('kenmore','Kenmore'),
        ('kitchenaid','KitchenAid'),
        ('lennox','Lennox'),
        ('lg','LG'),
        ('lochinvar','Lochinvar'),
        ('ma-line','MA-Line'),
        ('magic_chef','Magic Chef'),
        ('mastercool','Mastercool'),
        ('maytag','Maytag'),
        ('modern_maid','MODERN MAID'),
        ('monarch','MONARCH'),
        ('nordyne','Nordyne'),
        ('packard','Packard'),
        ('panasonic','Panasonic'),
        ('parts_connect','Parts Connect'),
        ('peerless_premier','Peerless Premier'),
        ('performance_tool','Performance Tool'),
        ('proform','Proform'),
        ('rheem_ruud','Rheem / Ruud'),
        ('roper','Roper'),
        ('rotom','Rotom'),
        ('samsung','Samsung'),
        ('sanyo','Sanyo'),
        ('secop_nidec','Secop / Nidec'),
        ('sharp','Sharp'),
        ('sole','Sole'),
        ('southeast_specialties','Southeast Specialties'),
        ('speed_queen','Speed Queen'),
        ('subz','Sub Zero'),
        ('supco','Supco'),
        ('tappan','Tappan'),
        ('thermador','Thermador'),
        ('titan','Titan'),
        ('trane','Trane'),
        ('u-line','U-LINE'),
        ('universal','Universal Replacement'),
        ('vapco','Vapco'),
        ('viking','Viking'),
        ('water filter tree','Water Filter Tree'),
        ('westinghouse','WESTINGHOUSE'),
        ('whirlpool','Whirlpool'),
        ('whirlpool_maytag','Whirlpool Maytag'),
        ('york','York')], string="Google Brand")
    
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
     
    def update_google_id_and_gtin(self):
        self.env.cr.execute("""select google_id from product_template order by google_id desc nulls last limit 1""")
        update_result_google_id = self.env.cr.fetchone()
        update_id_num = int(update_result_google_id[0])
        update_google_id = update_id_num + 1
        self.google_id = update_google_id
        self.google_gtin = self.generate_gtin(self.google_id)        
        self.save_field = "[Record Saved]"
        return
