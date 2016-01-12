# -*- coding: utf-8 -*-
from osv import osv, fields


class res_partner_address(osv.osv):
    _inherit = 'res.partner.address'
    _name = 'res.partner.address'

    _columns = {
        'address_number': fields.char(
            string='Number',
            size=10,
            ),
        'address_block': fields.char(
            string='Block',
            size=10,
            ),
        'address_rt': fields.char(
            string='RT',
            size=10,
            ),
        'address_rw': fields.char(
            string='RW',
            size=10,
            ),
        'address_kec': fields.char(
            string='Kecamatan',
            size=100,
            ),
        'address_kel': fields.char(
            string='Kelurahan',
            size=100,
            ),
    }

res_partner_address()
