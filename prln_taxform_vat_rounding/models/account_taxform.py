# -*- coding: utf-8 -*-
# © 2015 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from osv import osv, fields
import decimal_precision as dp


class account_taxform(osv.osv):
    _name = 'account.taxform'
    _inherit = 'account.taxform'

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj_dec = self.pool.get('decimal.precision')
        rounding = obj_dec.precision_get(cr, uid, 'Account')
        for taxform in self.browse(cr, uid, ids, context=context):
            res[taxform.id] = {
                'amount_full': 0.0,
                'amount_untaxed': 0.0,
                'amount_discount': 0.0,
                'amount_base': 0.0,
            }

            for line in taxform.taxform_line:
                res[taxform.id]['amount_full'] += line.price_subtotal_base
                res[taxform.id]['amount_discount'] += round(line.discount_amount_total, rounding)
                res[taxform.id]['amount_untaxed'] += line.price_subtotal
                res[taxform.id]['amount_base'] = res[taxform.id]['amount_full'] \
                    - res[taxform.id]['amount_discount'] \
                    + taxform['amount_advance_payment']
        return res

    _columns = {
        'amount_full': fields.function(
            fnct=_amount_all,
            digits_compute=dp.get_precision('Account'),
            string='Full Amount',
            store={
                'account.taxform': (lambda self, cr, uid, ids, c={}: ids, [
                    'taxform_line'], 20),
            },
            multi='all'),
        'amount_untaxed': fields.function(
            fnct=_amount_all,
            digits_compute=dp.get_precision('Account'),
            string='Untaxed',
            store={
                'account.taxform': (lambda self, cr, uid, ids, c={}: ids, [
                    'taxform_line'], 20),
            },
            multi='all'),
        'amount_discount': fields.function(
            fnct=_amount_all,
            digits_compute=dp.get_precision('Account'),
            string='Discount',
            store={
                'account.taxform': (lambda self, cr, uid, ids, c={}: ids, [
                    'taxform_line'], 20),
            },
            multi='all'),
        'amount_base': fields.function(
            fnct=_amount_all,
            digits_compute=dp.get_precision('Account'),
            string='Base',
            store={
                'account.taxform': (lambda self, cr, uid, ids, c={}: ids, [
                    'taxform_line'], 20),
            },
            multi='all'),
    }

class account_taxform_line(osv.osv):
    _name = 'account.taxform.line'
    _inherit = 'account.taxform.line'

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj_dec = self.pool.get('decimal.precision')
        rounding = obj_dec.precision_get(cr, uid, 'Account')
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'price_unit_base': 0.0,
                'price_subtotal_base': 0.0,
                'discount_amount': 0.0,
                'discount_amount_total': 0.0
                }
            inv_line = line.invoice_line_id
            res[line.id]['price_unit_base'] = inv_line.price_unit
            line_discount = inv_line.price_unit * (inv_line.discount / 100.00)
            res[line.id]['discount_amount'] = line_discount
            res[line.id]['discount_amount_total'] = (inv_line.price_unit * inv_line.quantity) * (inv_line.discount / 100.00)
            res[line.id]['price_subtotal_base'] = inv_line.price_subtotal_base
        return res



    _columns = {
        'price_unit_base': fields.function(
            fnct=_amount_all,
            multi='all',
            string='Base Price Unit',
            type='float',
            store=False,
            digits_compute=dp.get_precision('Account'),
            ),
        'price_subtotal_base': fields.function(
            fnct=_amount_all,
            multi='all',
            string='Base Subtotal',
            type='float',
            store=False,
            digits_compute=dp.get_precision('Account'),
            ),
        'discount_amount': fields.function(
            fnct=_amount_all,
            multi='all',
            string='Disc Amount Per Unit',
            type='float',
            store=False,
            digits_compute=dp.get_precision('Account'),
            ),
        'discount_amount_total': fields.function(
            fnct=_amount_all,
            multi='all',
            string='Discount Amount Total',
            type='float',
            store=False,
            digits_compute=dp.get_precision('Account'),
            ),
        }


