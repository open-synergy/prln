# -*- coding: utf-8 -*-

from osv import fields, osv
import decimal_precision as dp


class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'

    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        for c in self.pool.get('account.tax').compute_all(
                cr, uid, line.tax_id,
                line.price_unit * (1-(line.discount or 0.0)/100.0),
                line.product_uom_qty, line.order_id.partner_invoice_id.id,
                line.product_id, line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'amount_base': 0.0,
                'amount_discount': 0.0,
            }
            val = val1 = tax = 0.0
            vat = False
            for line in order.order_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
                if self._amount_line_tax(cr, uid, line, context) >= 0.0:
                    vat = True
            res[order.id]['amount_untaxed'] = val1
            res[order.id]['amount_base'] += line.price_subtotal_base
            res[order.id]['amount_discount'] += line.discount_amount_total
            if vat:
                tax = 0.1 * res[order.id]['amount_untaxed']
                tax = float(int(tax))
            res[order.id]['amount_tax'] = tax
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] \
                + res[order.id]['amount_tax']
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(
                cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'amount_untaxed': fields.function(
            fnct=_amount_all,
            digits_compute=dp.get_precision('Sale Price'),
            string='Untaxed Amount',
            store={
                'sale.order': (
                    lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, [
                    'price_unit', 'tax_id', 'discount',
                    'product_uom_qty',
                    ], 10),
                },
            multi='sums',
            help="The amount without tax.",
            ),
        'amount_tax': fields.function(
            fnct=_amount_all,
            digits_compute=dp.get_precision('Sale Price'),
            string='Taxes',
            store={
                'sale.order': (
                    lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, [
                    'price_unit', 'tax_id',
                    'discount', 'product_uom_qty',
                    ], 10),
                },
            multi='sums',
            help="The tax amount.",
            ),
        'amount_total': fields.function(
            fnct=_amount_all,
            digits_compute=dp.get_precision('Sale Price'),
            string='Total',
            store={
                'sale.order': (
                    lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, [
                    'price_unit', 'tax_id',
                    'discount', 'product_uom_qty',
                    ], 10),
                },
            multi='sums',
            help="The total amount."),
        'amount_base': fields.function(
            fnct=_amount_all,
            digits_compute=dp.get_precision('Sale Price'),
            string='Base',
            store=False,
            multi='sums',
            ),
        'amount_discount': fields.function(
            fnct=_amount_all,
            digits_compute=dp.get_precision('Sale Price'),
            string='Discount',
            store=False,
            multi='sums',
            ),
        }

class sale_order_line(osv.osv):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'price_subtotal': 0.0,
                'price_unit_base': 0.0,
                'discount_amount': 0.0,
                'discount_amount_total': 0.0,
                'price_subtotal_base': 0.0,
                }

            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(
                cr, uid, line.tax_id, price, 1.0, 
                line.order_id.partner_invoice_id.id, 
                line.product_id, line.order_id.partner_id)
            res[line.id]['price_subtotal'] = taxes['total'] * line.product_uom_qty
            res[line.id]['price_unit_base'] = taxes['total'] * (100.00/(100.00-line.discount))
            res[line.id]['price_subtotal_base'] = res[line.id]['price_unit_base'] * line.product_uom_qty
            res[line.id]['price_subtotal'] = taxes['total'] * line.product_uom_qty
            res[line.id]['discount_amount'] = res[line.id]['price_unit_base'] - taxes['total']
            res[line.id]['discount_amount_total'] = res[line.id]['discount_amount'] * line.product_uom_qty
        return res

    _columns = {
        'price_subtotal': fields.function(
            fnct=_amount_line, 
            string='Subtotal', 
            digits_compute= dp.get_precision('Sale Price'),
            store=False,
            multi='subtotal',
            ),
        'price_unit_base': fields.function(
            fnct=_amount_line, 
            string='Base Unit Price', 
            digits_compute= dp.get_precision('Sale Price'),
            store=False,
            multi='subtotal',
            ),
        'discount_amount': fields.function(
            fnct=_amount_line, 
            string='Amount Disc Per Unit', 
            digits_compute= dp.get_precision('Sale Price'),
            store=False,
            multi='subtotal',
            ),
        'discount_amount_total': fields.function(
            fnct=_amount_line, 
            string='Amount Disc', 
            digits_compute= dp.get_precision('Sale Price'),
            store=False,
            multi='subtotal',
            ),
        'price_subtotal_base': fields.function(
            fnct=_amount_line, 
            string='Base Subtotal', 
            digits_compute= dp.get_precision('Sale Price'),
            store=False,
            multi='subtotal',
            ),
        }
