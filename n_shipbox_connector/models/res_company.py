# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import requests
import base64
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime, timedelta



class ResCompany(models.Model):
    _inherit = 'res.company'

    shipox_country_id = fields.Many2one('shipbox.country', string='Shipox Country')
    shipox_city_id = fields.Many2one('shipbox.city', string='Shipox City')
    
    shipox_data = fields.Selection([
        ('manually', 'Manually'),
        ('instance_create', 'Instant Post'),
        ('schedule', 'Auto Schedule'),], string="Shipox Upload Type", default="instance_create")
    
    
    
        
         