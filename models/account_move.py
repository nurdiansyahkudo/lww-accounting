from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    no_journal = fields.Char(string="Journal Number", store=True)
    no_invoice = fields.Char(string="Form Number", store=True)