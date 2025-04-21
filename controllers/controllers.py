# -*- coding: utf-8 -*-
# from odoo import http


# class LwwAccounting(http.Controller):
#     @http.route('/lww_accounting/lww_accounting', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lww_accounting/lww_accounting/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('lww_accounting.listing', {
#             'root': '/lww_accounting/lww_accounting',
#             'objects': http.request.env['lww_accounting.lww_accounting'].search([]),
#         })

#     @http.route('/lww_accounting/lww_accounting/objects/<model("lww_accounting.lww_accounting"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lww_accounting.object', {
#             'object': obj
#         })

