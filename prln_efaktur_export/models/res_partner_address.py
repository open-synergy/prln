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
        'address_rt': fields.char(
            string='RT',
            ),
        'address_rw': fields.char(
            string='RW',
            ),
        'address_kec': fields.char(
            string='Kecamatan',
            ),
        'address_kel': fields.char(
            string='Kelurahan',
            ),
    }

res_partner_address()
