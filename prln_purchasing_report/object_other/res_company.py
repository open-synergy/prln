# -*- coding: utf-8 -*-
# © 2015 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from osv import osv
from osv import fields


class res_company(osv.osv):
    _name = 'res.company'
    _inherit = 'res.company'

    _columns = {
        'tax_ids': fields.many2many(
            string='Taxes',
            obj='account.tax',
            rel='company_account_tax_rel',
            id1='company_id',
            id2='tax_id',
        ),
    }

res_company()
