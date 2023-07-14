# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import requests
import base64
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime, timedelta



class ShipboxCity(models.Model):
    _name = 'shipbox.city'
    _description = 'Shipbox City'

    
    name = fields.Char(string='Name' , required=True)
    shipbox_id = fields.Char(string='ShipBox ID' , required=True)
    description = fields.Char(string='Description')
    
    
        
         