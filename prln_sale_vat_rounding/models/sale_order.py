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
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = tax = 0.0
            cur = order.pricelist_id.currency_id
            vat = False
            for line in order.order_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
                if self._amount_line_tax(cr, uid, line, context) >= 0.0:
                    vat = True
            # res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            # res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            # res[order.id]['amount_untaxed'] = float(int(val1))
            res[order.id]['amount_untaxed'] = val1
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
        }

class sale_order_line(osv.osv):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            # taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, 1.0, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)
            # cur = line.order_id.pricelist_id.currency_id
            res[line.id] = taxes['total'] * line.product_uom_qty
            # res[line.id] = taxes['total']
            # res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'] * line.product_uom_qty)
        return res

    _columns = {
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Sale Price')),
        }
