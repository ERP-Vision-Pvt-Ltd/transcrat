# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import requests
import base64
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime, timedelta



class ShipboxCountry(models.Model):
    _name = 'shipbox.country'
    _description = 'Shipbox Country'

    
    name = fields.Char(string='Name' , required=True)
    shipbox_id = fields.Char(string='ShipBox ID' , required=True)
    description = fields.Char(string='Description')
    
    
        
         