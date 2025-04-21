# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class lww_accounting(models.Model):
#     _name = 'lww_accounting.lww_accounting'
#     _description = 'lww_accounting.lww_accounting'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

