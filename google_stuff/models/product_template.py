# -*- coding: utf-8 -*-
from odoo import models, fields, _
import math
import secrets

class googleModel(models.Model):
    _inherit = 'product.template'
    # define our fields    
    exclude_from_google_export = fields.Boolean("Do NOT include in Google feed", default=False)
    googleid_lock = fields.Char("Google Lock")
    google_id = fields.Integer("Google ID")
    google_gtin = fields.Char("Google GTIN UPC")
    google_brand = fields.Char("Brand name for Google")
    google_category = fields.Integer("Google Category ID number.")
    
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

    def generate_google_id(self, current_rec_id):
        working_record = self.current_rec_id
        self._cr.execute('SELECT "google_id", "google_gtin", "googleid_lock", "id" from product_template ORDER BY google_id ASC LIMIT 1;')
        data = self._cr.fetchone()
        google_lock = secrets.token_hex(15)
        last_google_id = data[0]
        last_google_lock = data[2]
        last_record_id = data[3]
        if last_google_lock == "" or last_google_lock == 0 or last_google_lock is None:
            new_google_id = last_google_id + 1 
            print("SQL:")
            print(f'UPDATE product_template SET googleid_lock = "{google_lock}" WHERE id = {last_record_id}; UPDATE product_template SET google_id = "{new_google_id}" WHERE id = {working_record};')
            # self._cr.execute(f'UPDATE product_template SET google_lock = "{google_lock}" WHERE id = {last_record_id}; UPDATE product_template SET google_id = "{new_google_id}" WHERE id = {current_rec_id};')
            return new_google_id
    
    def update_google_id_and_gtin(self):
        current_record_id = int(self.id)
        if self.google_id == 0 or self.google_id == "":  
            print("Passed Record ID: ", current_record_id)
            self.google_id = self.generate_google_id(current_record_id)
        if self.google_gtin == 0 or self.google_gtin == "":
            self.google_gtin = self.generate_gtin(self.google_id)
        
        