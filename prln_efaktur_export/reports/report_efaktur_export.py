# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Andhitia Rama
#    Copyright 2015 OpenSynergy Indonesia
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from report import report_sxw
from datetime import datetime


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
        if not taxform_ids:
            return self.lines

        for o in obj_taxform.browse(cr, uid, taxform_ids):
            dt_masa_pajak = datetime.strptime(o.invoice_date, '%Y-%m-%d')
            masa_pajak = dt_masa_pajak.strftime('%m')
            dt_tahun_pajak = datetime.strptime(o.invoice_date, '%Y-%m-%d')
            tahun_pajak = dt_tahun_pajak.strftime('%Y')
            dt_tanggal_pajak = datetime.strptime(o.invoice_date, '%Y-%m-%d')
            tanggal_pajak = dt_tanggal_pajak.strftime('%d/%m/%Y')

            partner_address = o.partner_address_id.street
            partner_zip = o.partner_address_id.zip
            partner_phone = o.partner_address_id.phone
            taxform_id = '%s%s%s' % (o.trx_code, tahun_pajak, o.taxform_id)
            partner_npwp = o.partner_npwp.value.replace("-", "")
            partner_npwp = partner_npwp.replace(".", "")

            data = {
                'taxform_id': taxform_id,
                'company_name': o.company_id.name,
                'company_npwp': o.company_npwp,
                'masa_pajak': masa_pajak,
                'tahun_pajak': tahun_pajak,
                'tanggal_faktur': tanggal_pajak,
                'alamat_lengkap': o.company_address_id.street,
                'jumlah_dpp': 0.0,
                'jumlah_ppn': 0.0,
                'jumlah_ppnbm': 0.0,
                'referensi': o.invoice_id.number,
                'partner_npwp': partner_npwp,
                'partner_name': o.partner_id or '-',
                'partner_street':  partner_address or '-',
                'partner_zip': partner_zip or '-',
                'partner_phone': partner_phone or '-',
                'details_lt': [],
                }

            if o.taxform_line:
                for detail in o.taxform_line:
                    data['jumlah_dpp'] += detail.price_subtotal
                    price_before_disc = detail.price_subtotal * \
                            (100.00 / (100.00 - detail.discount))
                    price_unit = price_before_disc / detail.quantity
                    price_unit = round(price_unit,2)
                    amount_untaxed = price_unit * detail.quantity

                    if detail.discount:
                        discount = detail.discount
                    else:
                        discount = 0

                    amount_discount = amount_untaxed * (discount / 100.0)
                    # dpp = amount_untaxed - amount_discount
                    dpp = detail.price_subtotal
                    ppn = dpp * 0.1

                    data1 = {
                        'product_code': detail.product_id.default_code,
                        'product_name': detail.product_id.product_tmpl_id.name,
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
                data['jumlah_ppn'] = 0.1 * data['jumlah_dpp']

            self.lines.append(data)
        return self.lines
