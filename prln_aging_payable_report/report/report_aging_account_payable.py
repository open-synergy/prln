# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Michael Viriyananda
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

from datetime import datetime, date, time
import time
from report import report_sxw


class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_invoice_date_from': self.get_invoice_date_from,
            'get_invoice_date_to': self.get_invoice_date_to,
            'get_companies': self.get_companies,
            'get_supplier': self.get_supplier,
            'get_lines': self.lines
        })

    def convert_date(self, date):
        convert_date = ''
        nama_bulan = ''

        if date:

            date_tahun = date[0:4]
            date_bulan = date[5:7]
            date_tanggal = date[8:10]

            bulan = {
                    '01': 'Januari',
                    '02': 'Februari',
                    '03': 'Maret',
                    '04': 'April',
                    '05': 'Mei',
                    '06': 'Juni',
                    '07': 'Juli',
                    '08': 'Agustus',
                    '09': 'September',
                    '10': 'Oktober',
                    '11': 'November',
                    '12': 'Desember'
                    }

            nama_bulan = bulan.get(date_bulan, False)

            convert_date = date_tanggal + ' ' + nama_bulan + ' ' + date_tahun

        return convert_date

    def get_invoice_date_from(self):
        invoice_date_from = self.localcontext['data']['form']['invoice_date_from']
        convert_date_from = self.convert_date(invoice_date_from)
        return convert_date_from

    def get_invoice_date_to(self):
        invoice_date_to = self.localcontext['data']['form']['invoice_date_to']
        convert_date_to = self.convert_date(invoice_date_to)

        return convert_date_to

    def get_companies(self):
        line_companies_ids = []

        obj_company = self.pool.get('res.company')

        company_ids = self.localcontext['data']['form']['company_ids']

        if company_ids:

            for company_id in obj_company.search(self.cr, self.uid, [('id', '=', company_ids)]):
                if company_id:
                    company = obj_company.browse(self.cr, self.uid, company_id)
                    res = {
                        'name': company.name,
                        'id': company.id
                    }
                    line_companies_ids.append(res)

        return line_companies_ids

    def get_supplier(self):
        line_supplier_ids = []
        no = 1

        obj_supplier = self.pool.get('res.partner')

        supplier_ids = self.localcontext['data']['form']['supplier_ids']

        if supplier_ids:

            for supplier_id in obj_supplier.search(self.cr, self.uid, [('id', '=', supplier_ids)]):
                if supplier_id:
                    supplier = obj_supplier.browse(self.cr, self.uid, supplier_id)
                    res = {
                        'no': no,
                        'name': supplier.name,
                        'id': supplier.id
                    }
                    line_supplier_ids.append(res)
                    no += 1

        return line_supplier_ids

    def lines(self, company_id, supplier_id):
        lines = []
        invoice_date_from = self.localcontext['data']['form']['invoice_date_from']
        invoice_date_to = self.localcontext['data']['form']['invoice_date_to']

        ord_date = datetime.strptime(date, '%Y-%m-%d').toordinal()

        obj_account_move = self.pool.get('account.move')
        obj_account_move_line = self.pool.get('account.move.line')
        obj_account_period = self.pool.get('account.period')

        period_id = obj_account_period.find(self.cr, self.uid, invoice_date_from)

        kriteria_account_move = [
            ('company_id', '=', company_id),
            ('partner_id', '=', supplier_id),
            ('state', '=', 'posted'),
            ('period_id', '=', period_id)
        ]

        move_ids = obj_account_move.search(self.cr, self.uid, kriteria_account_move)

        if move_ids:
            for move_id in move_ids:
                if move_id:

                    kriteria_account_move_line = [('move_id', '=', move_id), ('credit', '>', 0), ('account_id.type', '=', 'payable')]

                    move_line_ids = obj_account_move_line.search(self.cr, self.uid, kriteria_account_move_line)

                    if move_line_ids:
                        for move_line_id in move_line_ids:
                            move_line = obj_account_move_line.browse(self.cr, self.uid, move_line_id)

                            if invoice_date_from <= move_line.date_maturity and invoice_date_to >= move_line.date_maturity:
                                res = {
                                    'name': move_line.move_id.name,
                                    'account_payable': move_line.credit,
                                    'current': move_line.credit,
                                    '1-30': False,
                                    '31-60': False,
                                    '61-90': False,
                                    '>=90': False
                                }
                                lines.append(res)

        return lines
