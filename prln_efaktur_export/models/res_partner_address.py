# -*- coding: utf-8 -*-
from osv import osv, fields


class res_partner_address(osv.osv):
    _inherit = 'res.partner.address'
    _name = 'res.partner.address' 

    _columns = {
        'address_number': fields.char(
            string='Number',
            ),
        'address_block': fields.char(
            string='Block',
            ),
    }


res_partner_address()
