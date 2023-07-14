# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import requests
import base64
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime, timedelta



class ShipboxConnector(models.Model):
    _name = 'shipbox.instance'
    _description = 'Shipbox Instance'

    
    name = fields.Char(string='Name' , required=True)
    auth_url = fields.Char(string='Auth URL' , required=True)
    order_url = fields.Char(string='Order URL' , required=True)
    username = fields.Char(string='Username' , required=True)
    password = fields.Char(string='Password' , required=True)
    company_id = fields.Many2one('res.company', string='Company')
    pkg_type_id = fields.Many2one('shipbox.service.type', string='Service Type', default=lambda self: self.env['shipbox.service.type'].search([('code','=','NEXT_DAY')], limit=1).id if self.env['shipbox.service.type'].search([], limit=1) else 0)
    delivered_status = fields.Char(string='Delivered Status', default='["test_format","test_status",]')
    token = fields.Char(string='Token')
    recipient_not_available = fields.Selection([
        ('do_not_deliver', 'Do Not Deliver'),
        ('leave_at_door', 'Leave At Door'),
        ('leave_with_concierge', 'Leave With Concierge'),], 
        string="Recipient Not Available",
                             default="do_not_deliver")
    payment_type = fields.Selection([
        ('credit_balance', 'Credit Balance'),
        ('cash', 'Cash'),
        ], 
        string="Payment Type",
                             default="credit_balance")
    payer = fields.Selection([
        ('recipient', 'Recipient'),
        ('sender', 'Sender'),
        ], 
        string="Payer",
                             default="recipient")
    
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('close', 'Closed'),], string="Status",
                             default="draft")
    
    
    
    def action_check_connection(self):
        for line in self:
            values = {
              "username": line.username,
              "password": line.password,
              "remember_me": True
            }
            headers = {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
            
            response = requests.post(line.auth_url, data=json.dumps(values), headers=headers)
            auth_token = response.json()
            if response.status_code==200:
                raise UserError('Successfully connected to Shipbox Instance! ')
            else:
                raise UserError('Connection Refused! Credentials are not configured Correctly! ')

    
    def action_active(self):
        for line in self:
            line.state='active'
            
    def action_reset(self):
        for line in self:
            line.state='draft'        
    
    def action_get_master_data(self):
        instance = self.env['shipbox.instance'].search([])
        headers = {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
        for line in instance: 
            values = {
              "username": line.username,
              "password": line.password,
              "remember_me": True
            }
            response = requests.post(line.auth_url, data=json.dumps(values), headers=headers)
            auth_token = response.json()
            line.token = 'Bearer '+str(auth_token['data']['id_token'])
            headers = {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
              'Authorization': line.token
            }
            neighborhoods = requests.get('https://prodapi.shipox.com/api/v2/customer/neighborhoods?', headers=headers)
            neighborhoods_list = neighborhoods.json()
            
            for neighborhoods in neighborhoods_list['data']['list']:
                city_list = self.env['shipbox.neighborhoods'].search([('shipbox_id','=',neighborhoods['id'])])
                if not city_list:
                    neighborhoods_vals = {
                        'name': neighborhoods['name'],
                        'shipbox_id': neighborhoods['id'],
                    }
                    country = self.env['shipbox.neighborhoods'].create(neighborhoods_vals)

            service_typeresponse = requests.get('https://prodapi.shipox.com/api/v1/service_types', headers=headers)
            service_type_list = service_typeresponse.json()
            # city_list = 
            for service_type in service_type_list['data']['list']:
                service_type_list = self.env['shipbox.service.type'].search([('shipbox_id','=',service_type['id'])])
                if not service_type_list:
                    service_type_vals = {
                        'name': service_type['name'],
                         'code': service_type['code'], 
                        'sorder': service_type['sorder'],
                        'shipbox_id': service_type['id'],
                    }
                    country = self.env['shipbox.service.type'].create(service_type_vals)    

            country_response = requests.get('https://prodapi.shipox.com/api/v2/customer/countries?', headers=headers)
            country_list = country_response.json()
            # city_list = 
            for country in country_list['data']['list']:
                country_list = self.env['shipbox.country'].search([('shipbox_id','=',country['id'])])
                if not country_list:
                    country_vals = {
                        'name': country['name'],
                        'shipbox_id': country['id'],
                    }
                    country = self.env['shipbox.country'].create(country_vals)

            city_response = requests.get('https://prodapi.shipox.com/api/v2/customer/cities?', headers=headers)
            city_list = city_response.json()
            for city in city_list['data']['list']:
                city_list = self.env['shipbox.city'].search([('shipbox_id','=',city['id'])])
                if not city_list:
                    city_vals = {
                        'name': city['name'],
                        'shipbox_id': city['id'],
                    }
                    city = self.env['shipbox.city'].create(city_vals)  

                
                
    def action_post_data(self): 
        instance = self.env['shipbox.instance'].search([('company_id','=', False)], limit=1)
        headers = {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
        }
        pickings = self.env['stock.picking'].search([ ('sale_id', '!=', False),('sync_shipox_status','=',False),('state','=','assigned') ])
        for picking in pickings:
            if picking.company_id.shipox_data=='schedule' and picking.picking_type_code=='outgoing':
                instance = self.env['shipbox.instance'].search([('company_id','=', picking.company_id.id)], limit=1)
                if not instance:
                    instance = self.env['shipbox.instance'].search([('company_id','=', False)], limit=1) 
                auth_values = {
                  "username": instance.username,
                  "password": instance.password,
                  "remember_me": True
                }    
                token_response = requests.post(instance.auth_url, data=json.dumps(auth_values), headers=headers)
                auth_token = token_response.json()   
                instance.token = 'Bearer '+str(auth_token['data']['id_token'])
                headers = {
                  'Content-Type': 'application/json',
                  'Accept': 'application/json',
                  'Authorization': instance.token
                }
                if picking.partner_id.shipox_country_id and picking.partner_id.shipox_city_id and picking.company_id.shipox_country_id and picking.company_id.shipox_city_id:
                    parcel_value = 0
                    parcel_weight = 0
                    parcel_widthall = 0
                    charge_item_list = []
                    line_item_list = []
                    paid_order_data = False
                    paid_transaction = self.env['payment.transaction'].search([('reference','=',picking.sale_id.name),('state','=','done')], limit=1)
                    if paid_transaction:
                        paid_order_data = True
                    charge_item_list.append({
                        "charge_type": "cod","charge": picking.sale_id.amount_total, "payer": "recipient", "paid": paid_order_data,
                    })
                    note_description=''
                    for picking_line in picking.sale_id.order_line:
                        note_description = note_description +' ,'+ str(picking_line.product_id.name)
                        parcel_value += picking_line.product_uom_qty
                        line_item_list.append({"name": picking_line.product_id.name,
                                                "ean13_code": picking_line.product_id.default_code,
                                                "origin_country": "Kuwait",
                                                "price_per_unit": picking_line.price_unit,
                                                "price": picking_line.price_subtotal,
                                                "quantity": picking_line.product_uom_qty,
                                                "tax_code": "00000",
                                                "desc": picking_line.name,
                                                "weight": round(picking_line.product_id.weight*picking_line.product_uom_qty)})
                        parcel_weight += round(picking_line.product_id.weight*picking_line.product_uom_qty)
                        parcel_widthall += round((picking_line.product_id.weight*picking_line.product_uom_qty)*0.3)
                    values = {
                      "sender_data": {
                        "address_type": "residential",
                        "name": picking.company_id.name,
                        "email": picking.company_id.email,
                        "phone": picking.company_id.phone,
                        "street": str(picking.company_id.street)+' '+str(picking.company_id.street2) ,  
                        "city": {"id": 	picking.company_id.shipox_city_id.shipbox_id},
                        "country": {"id": picking.company_id.shipox_country_id.shipbox_id},
                      },
                      "recipient_data": {
                        "address_type": "residential",
                        "name": picking.partner_id.name,
                        "email": picking.partner_id.email,
                        "phone": picking.partner_id.phone,
                        "street": str(picking.partner_id.street)+', '+str(picking.partner_id.street2) ,  
                        "city": {"id": 	picking.partner_id.shipox_city_id.shipbox_id},
                        "country": {"id": picking.partner_id.shipox_country_id.shipbox_id},
                      },
                      "dimensions": {
                        "weight": parcel_weight,
                        "width": parcel_widthall,
                        "length": parcel_widthall,
                        "height": parcel_widthall,
                        "unit": "METRIC",
                        "domestic": False
                      },
                      "package_type": {
                      "courier_type": instance.pkg_type_id.code if instance.pkg_type_id else "NEXT_DAY"
                      },
                      "charge_items": charge_item_list,
                      "recipient_not_available": instance.recipient_not_available,
                      "payment_type": instance.payment_type,
                      "payer": instance.payer,
                      "parcel_value": picking.sale_id.amount_total,
                      "fragile": True,
                      "note": note_description,
                      "piece_count": "",
                      "force_create": True,
                      "reference_id": picking.sale_id.name
                    }        
                    order = requests.post(instance.order_url, headers=headers , data=json.dumps(values))
                    order_res_occr = order.json()
                    if order_res_occr['data'] and 'order_number' in order_res_occr['data']:
                        picking.update({'sync_shipox_status': True, 'shipox_order_number': order_res_occr['data']['order_number'],})

         
        
        
        
        
        
    def action_get_and_update_picking_status(self):
        instance = self.env['shipbox.instance'].search([('company_id','=', False)], limit=1)
        headers = {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
        }
        
        pickings = self.env['stock.picking'].search([ ('shipox_order_number','!=',''),('sale_id', '!=', False),('sync_shipox_status','=',True),('state','=','assigned') ])
        for picking in pickings:
            instance = self.env['shipbox.instance'].search([('company_id','=', picking.company_id.id)], limit=1)
            if not instance:
                instance = self.env['shipbox.instance'].search([('company_id','=', False)], limit=1)  
            auth_values = {
              "username": instance.username,
              "password": instance.password,
              "remember_me": True
            }    
            token_response = requests.post(instance.auth_url, data=json.dumps(auth_values), headers=headers)
            auth_token = token_response.json()
            instance.token = 'Bearer '+str(auth_token['data']['id_token'])    
            headers = {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
              'Authorization': instance.token
            }
            url = 'https://prodapi.shipox.com/api/v1/customer/order/'+str(picking.shipox_order_number)+'/history_items'
            get_order = requests.get(url, headers=headers)
            uniq_order = get_order.json()
            uniq_order_list = []
            uniq_order_list = uniq_order['data']['list']
            for order_track in uniq_order_list:
                if order_track['status'] in instance.delivered_status:
                    for moveline in picking.move_ids_without_package:
                        moveline.update({
                            'quantity_done': moveline.product_uom_qty,
                        })
            picking.button_validate()
                        
            
        
            
            