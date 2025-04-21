# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    code = fields.Char(
        string='Short Code',
        size=15,
        compute='_compute_code', readonly=False, store=True,
        required=True, precompute=True,
        help="Shorter name used for display. "
             "The journal entries of this journal will also be named using this prefix by default."
    )

