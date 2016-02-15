# -*- coding: utf-8 -*-

from osv import osv


class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    def buton_reset_taxes(self, cr, uid, ids, context=None):

        super(account_invoice, self).button_reset(cr, uid, ids, context)
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
                ait_obj.create(cr, uid, taxe)
            # Update the stored value (fields.function), so we write to trigger recompute
            self.pool.get('account.invoice').write(cr, uid, ids, {'invoice_line':[]}, context=ctx)


