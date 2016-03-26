# -*- coding: utf-8 -*-
# © 2015 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from report import report_sxw
from datetime import datetime
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_EVEN


class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.lines = []
        self.localcontext.update(
            {
                'get_lines': self.get_lines
            }
        )

    def get_lines(self):
        pool = self.pool
        cr = self.cr
        uid = self.uid
        obj_taxform = pool.get('account.taxform')
        taxform_ids = self.localcontext['data']['form'].get('taxform_ids', [])

        ADR = "%s BLOK %s NO.%s RT.%s RW.%s Kel.%s Kec.%s Kota/Kab %s %s %s"

        if not taxform_ids:
            return self.lines

        for o in obj_taxform.browse(cr, uid, taxform_ids):
            dt_masa_pajak = datetime.strptime(o.invoice_date, '%Y-%m-%d')
            masa_pajak = dt_masa_pajak.strftime('%m')
            masa_pajak = int(masa_pajak)
            dt_tahun_pajak = datetime.strptime(o.invoice_date, '%Y-%m-%d')
            tahun_pajak = dt_tahun_pajak.strftime('%Y')
            dt_tanggal_pajak = datetime.strptime(o.invoice_date, '%Y-%m-%d')
            tanggal_pajak = dt_tanggal_pajak.strftime('%d/%m/%Y')

            address = o.partner_address_id
            partner_address = ADR % (
                address.street,
                address.address_block or '-',
                address.address_number or '-',
                address.address_rt or '-',
                address.address_rw or '-',
                address.address_kel or '-',
                address.address_kec or '-',
                address.city or '-',
                address.state_id and address.state_id.name or '-',
                address.zip or ''
            )

            partner_zip = o.partner_address_id.zip
            partner_phone = o.partner_address_id.phone

            taxform_id = '%s%s' % (
                o.branch_code or '', o.taxform_id)

            taxform_id = taxform_id.replace(".", "")

            partner_npwp = o.partner_npwp.value.replace("-", "")
            partner_npwp = partner_npwp.replace(".", "")
            partner_title = o.partner_id.title and \
                o.partner_id.title.name or ''
            partner_name = '%s %s' % (
                partner_title, o.partner_id.name)
            partner_name = partner_name.strip()

            data = {
                'taxform_id': taxform_id,
                'company_name': o.company_id.name,
                'company_npwp': o.company_npwp,
                'trx_code': o.trx_code,
                'masa_pajak': masa_pajak,
                'tahun_pajak': tahun_pajak,
                'tanggal_faktur': tanggal_pajak,
                'alamat_lengkap': o.company_address_id.street,
                'jumlah_dpp': Decimal(0.0),
                'jumlah_ppn': Decimal(0.0),
                'jumlah_ppnbm': 0.0,
                'referensi': o.invoice_id.number,
                'partner_npwp': partner_npwp,
                'partner_name': partner_name,
                'partner_street':  partner_address or '-',
                'partner_zip': partner_zip or '-',
                'partner_phone': partner_phone or '-',
                'details_lt': [],
            }

            if o.taxform_line:
                for detail in o.taxform_line:
                    if detail.discount:
                        discount = Decimal(detail.discount)
                    else:
                        discount = Decimal(0.0)

                    price_subtotal = Decimal(detail.price_subtotal)
                    quantity = Decimal(detail.quantity)
                    data['jumlah_dpp'] += price_subtotal
                    price_before_disc = price_subtotal * \
                        (Decimal(100.00) / (Decimal(100.00) - discount))
                    price_unit = price_before_disc / quantity

                    price_unit = Decimal(
                        price_unit.quantize(
                            Decimal('.01'), rounding=ROUND_HALF_EVEN))
                    amount_untaxed = price_unit * quantity
                    amount_untaxed = Decimal(
                        amount_untaxed.quantize(
                            Decimal('.01'), rounding=ROUND_HALF_EVEN))

                    amount_discount = amount_untaxed * (
                        discount / Decimal(100.0))
                    amount_discount = Decimal(
                        amount_discount.quantize(
                            Decimal('.01'), rounding=ROUND_HALF_EVEN))
                    dpp = price_subtotal
                    dpp = Decimal(
                        dpp.quantize(
                            Decimal('.01'), rounding=ROUND_HALF_EVEN))
                    ppn = dpp * Decimal(0.1)
                    ppn = Decimal(
                        ppn.quantize(
                            Decimal('.001'), rounding=ROUND_HALF_EVEN))

                    data['jumlah_ppn'] += ppn

                    product_name = detail.product_id.product_tmpl_id.name
                    u = u'\N{DEGREE SIGN}'
                    product_name = product_name.replace(u, '')
                    product_name = product_name.replace('"', '""')

                    data1 = {
                        'product_code': detail.product_id.default_code,
                        'product_name': product_name,
                        'price_unit': price_unit,
                        'qty': detail.quantity,
                        'amount_untaxed': amount_untaxed,
                        'discount': amount_discount,
                        'dpp': dpp,
                        'ppn': ppn,
                        'tarif_ppnbm': 0,
                        'ppnbm': 0
                    }
                    data['details_lt'].append(data1)

                data['jumlah_ppn'] = Decimal(
                    data['jumlah_ppn'].quantize(
                        Decimal('1.'), rounding=ROUND_DOWN))

                data['jumlah_dpp'] = Decimal(
                    data['jumlah_dpp'].quantize(
                        Decimal('1.'), rounding=ROUND_DOWN))
            self.lines.append(data)
        return self.lines
