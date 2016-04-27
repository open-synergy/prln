# -*- coding: utf-8 -*-
# © 2015 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from osv import fields, osv
from tools.translate import _
import netsvc


class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'

    _columns = {
        'credit_limit': fields.float(
            string='Credit Limit',
            ),
        }

    def button_check_limit(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        obj_sale = self.pool.get('sale.order')

        for order in obj_sale.browse(cr, uid, ids):
            self._check_limit(cr, uid, order)

    def _check_limit(self, cr, uid, order):
        if order.partner_id.credit_limit < (order.partner_id.credit + order.amount_total):
            raise osv.except_osv(_('Warning'),_('Insufficient Limit'))

        wkf_service = netsvc.LocalService('workflow')
        wkf_service.trg_validate(uid, 'sale.order', order.id, 'order_confirm', cr)



