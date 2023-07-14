# -*- coding: utf-8 -*-
# from odoo import http


# class NnShipboxConnector(http.Controller):
#     @http.route('/n_shipbox_connector/n_shipbox_connector', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/n_shipbox_connector/n_shipbox_connector/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('n_shipbox_connector.listing', {
#             'root': '/n_shipbox_connector/n_shipbox_connector',
#             'objects': http.request.env['n_shipbox_connector.n_shipbox_connector'].search([]),
#         })

#     @http.route('/n_shipbox_connector/n_shipbox_connector/objects/<model("n_shipbox_connector.n_shipbox_connector"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('n_shipbox_connector.object', {
#             'object': obj
#         })
