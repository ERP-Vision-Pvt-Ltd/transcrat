# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import requests
import base64
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime, timedelta



class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sync_shipox_status = fields.Boolean(string='Posted to Shipox')
    shipox_order_number = fields.Char(string='Shipox Order Number')
    
    shipox_data = fields.Selection([
        ('manually', 'Manually'),
        ('instance_create', 'Instant Post'),
        ('schedule', 'Auto Schedule'),], string="Shipox Sync")
    
    
    @api.constrains('state')
    def _check_status_shipox(self):
        for line in self:
            line.shipox_data=line.company_id.shipox_data
            if line.state=='assigned' and line.company_id.shipox_data=='instance_create':
                line.action_post_shipox_data()
    
    
    def action_post_shipox_data(self): 
        instance = self.env['shipbox.instance'].search([('company_id','=', False)], limit=1)
        
        headers = {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
        }
        
        for picking in self:
            instance = self.env['shipbox.instance'].search([('company_id','=', picking.company_id.id)], limit=1)
            if not instance:
                instance = self.env['shipbox.instance'].search([('company_id','=', False)], limit=1) 
            if instance and picking.picking_type_code=='outgoing':    
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

                if not picking.company_id.shipox_city_id or not picking.company_id.shipox_country_id:
                    raise UserError('Please First select Shipox Company and City on Company Profile! '+str(picking.company_id.name))
                if not picking.partner_id.shipox_city_id or not picking.partner_id.shipox_country_id:
                    raise UserError('Please First select Shipox Company and City on Customer Profile! '+str(picking.partner_id.name))

                if picking.sale_id and picking.sync_shipox_status==False and picking.state=='assigned' and   picking.partner_id.shipox_country_id and picking.partner_id.shipox_city_id and picking.company_id.shipox_country_id and picking.company_id.shipox_city_id:
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
                      "reference_id": picking.sale_id.name,
                      "boxes": [{
                          "description": "Box",
                          "height": parcel_widthall,
                          "length": parcel_widthall,
                          "line_items": line_item_list,
                          "weight": parcel_weight,
                          "width": parcel_widthall,}],  
                    }   
                    order = requests.post(instance.order_url, headers=headers , data=json.dumps(values))
                    order_res_occr = order.json()
                    if order_res_occr['data'] and 'order_number' in order_res_occr['data']:
                        picking.update({'sync_shipox_status': True, 'shipox_order_number': order_res_occr['data']['order_number'],})

    
    
    
        
         