# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import requests
import base64
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime, timedelta



class ShipboxServiceType(models.Model):
    _name = 'shipbox.service.type'
    _description = 'Shipbox Service Type'

    
    name = fields.Char(string='Name' , required=True)
    code = fields.Char(string='Code' , required=True)
    sorder = fields.Char(string='Sorder' )
    shipbox_id = fields.Char(string='ShipBox ID' , required=True)
    description = fields.Char(string='Description')
    
    
        
         