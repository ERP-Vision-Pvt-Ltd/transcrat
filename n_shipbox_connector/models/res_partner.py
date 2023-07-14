# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import requests
import base64
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime, timedelta



class ResPartner(models.Model):
    _inherit = 'res.partner'

    shipox_country_id = fields.Many2one('shipbox.country', string='Shipox Country')
    shipox_city_id = fields.Many2one('shipbox.city', string='Shipox City')
    
    
    @api.constrains('country_id', 'city')
    def _check_country_and_city(self):
        for line in self:
            if line.country_id:
                shipx_country = self.env['shipbox.country'].search([('name','=',line.country_id.name)], limit=1)
                if shipx_country:
                    line.shipox_country_id = shipx_country.id
            if  line.city: 
                shipx_city = self.env['shipbox.city'].search([('name','=',line.city)], limit=1)
                if shipx_city:
                    line.shipox_city_id = shipx_city.id
            
        
    
    
        
         