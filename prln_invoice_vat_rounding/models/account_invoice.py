# -*- coding: utf-8 -*-

from osv import osv, fields
from tools.translate import _
import decimal_precision as dp


class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

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
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, 1.0, product=line.product_id, address_id=line.invoice_id.address_invoice_id, partner=line.invoice_id.partner_id)
            # taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, address_id=line.invoice_id.address_invoice_id, partner=line.invoice_id.partner_id)
            res[line.id] = taxes['total'] * line.quantity
            # if line.invoice_id:
            #     cur = line.invoice_id.currency_id
            #     res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res

    _columns = {
        'price_subtotal': fields.function(_amount_line, string='Subtotal', type="float",
            digits_compute= dp.get_precision('Account'), store=True),
    }
