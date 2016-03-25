# -*- coding: utf-8 -*-

from osv import osv, fields
from tools.translate import _
import decimal_precision as dp


class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0
            }
            for line in invoice.invoice_line:
                res[invoice.id]['amount_untaxed'] += line.price_subtotal
            for line in invoice.tax_line:
                res[invoice.id]['amount_tax'] += line.amount

            # eTax adjustment
            # res[invoice.id]['amount_untaxed'] = float(int(res[invoice.id]['amount_untaxed']))

            res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed']
        return res

    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()

    _columns = {

        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Tax',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        }


    def button_reset_taxes(self, cr, uid, ids, context=None):
        super(account_invoice, self).button_reset_taxes(cr, uid, ids, context)
        for invoice in self.browse(cr, uid, ids):
            if invoice.type != 'out_invoice':
                return True

            if context is None:
                context = {}
            ctx = context.copy()
            ait_obj = self.pool.get('account.invoice.tax')
            cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (invoice.id,))
            partner = self.browse(cr, uid, invoice.id, context=ctx).partner_id
            if partner.lang:
                ctx.update({'lang': partner.lang})
            for taxe in ait_obj.compute(cr, uid, invoice.id, context=ctx).values():

                # eTax adjustment
                taxe['base'] = invoice.amount_untaxed
                taxe['amount'] = float(int(0.1 * invoice.amount_untaxed))

                ait_obj.create(cr, uid, taxe)
            # Update the stored value (fields.function), so we write to trigger recompute
            self.pool.get('account.invoice').write(cr, uid, ids, {'invoice_line':[]}, context=ctx)


    def check_tax_lines(self, cr, uid, inv, compute_taxes, ait_obj):
        if not inv.tax_line:
            for tax in compute_taxes.values():
                ait_obj.create(cr, uid, tax)
        else:
            tax_key = []
            for tax in inv.tax_line:
                if tax.manual:
                    continue
                key = (tax.tax_code_id.id, tax.base_code_id.id, tax.account_id.id)
                tax_key.append(key)
                if not key in compute_taxes:
                    raise osv.except_osv(_('Warning !'), _('Global taxes defined, but they are not in invoice lines !'))
                # base = compute_taxes[key]['base']
                base = inv.amount_untaxed
                if abs(base - tax.base) > inv.company_id.currency_id.rounding:
                    raise osv.except_osv(_('Warning !'), _('Tax base different!\nClick on compute to update the tax base.'))
            for key in compute_taxes:
                if not key in tax_key:
                    raise osv.except_osv(_('Warning !'), _('Taxes are missing!\nClick on compute button.'))

class account_invoice_line(osv.osv):
    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        # cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            res[line.id] = {
                'price_unit_base': 0.0,
                'discount_amount': 0.0,
                'discount_amount_total': 0.0,
                'price_subtotal': 0.0,
                }

            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            taxes = tax_obj.compute_all(
                cr, uid, line.invoice_line_tax_id, 
                price, 1.0, product=line.product_id, 
                address_id=line.invoice_id.address_invoice_id, 
                partner=line.invoice_id.partner_id)
            # taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, address_id=line.invoice_id.address_invoice_id, partner=line.invoice_id.partner_id)
            res[line.id]['price_unit_base'] = taxes['total'] + ((line.discount/100.00) * taxes['total'])
            res[line.id]['price_subtotal'] = taxes['total'] * line.quantity
            # if line.invoice_id:
            #     cur = line.invoice_id.currency_id
            #     res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res

    _columns = {
        'price_unit_base': fields.function(
            _amount_line, 
            string='Base Unit Price', 
            type='float',
            digits_compute=dp.get_precision('Account'), 
            store=False,
            multi='subtotal',
            ),
        'discount_amount': fields.function(
            _amount_line, 
            string='Amount Disc Per Unit', 
            type='float',
            digits_compute=dp.get_precision('Account'), 
            store=False,
            multi='subtotal',
            ),
        'discount_amount_total': fields.function(
            _amount_line, 
            string='Amount Disc', 
            type='float',
            digits_compute=dp.get_precision('Account'), 
            store=False,
            multi='subtotal',
            ),
        'price_subtotal': fields.function(
            _amount_line, 
            string='Subtotal', 
            type='float',
            digits_compute=dp.get_precision('Account'), 
            store=True,
            multi='subtotal',
            ),
    }
