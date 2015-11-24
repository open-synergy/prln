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
        data_form = self.localcontext['data']['form']
        invoice_date_from = data_form['invoice_date_from']
        convert_date_from = self.convert_date(invoice_date_from)
        return convert_date_from

    def get_invoice_date_to(self):
        data_form = self.localcontext['data']['form']
        invoice_date_to = data_form['invoice_date_to']
        convert_date_to = self.convert_date(invoice_date_to)

        return convert_date_to

    def get_companies(self):
        line_companies_ids = []

        obj_company = self.pool.get('res.company')
        data_form = self.localcontext['data']['form']
        data_company_ids = data_form['company_ids']

        if data_company_ids:
            kriteria = [('id', '=', data_company_ids)]
            company_ids = obj_company.search(self.cr, self.uid, kriteria)
            for company_id in company_ids:
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

        data_form = self.localcontext['data']['form']

        data_supplier_ids = data_form['supplier_ids']

        if data_supplier_ids:
            kriteria = [('id', '=', data_supplier_ids)]
            supplier_ids = obj_supplier.search(self.cr, self.uid, kriteria)
            for supplier_id in supplier_ids:
                if supplier_id:
                    supp = obj_supplier.browse(self.cr, self.uid, supplier_id)
                    res = {
                        'no': no,
                        'name': supp.name,
                        'id': supp.id
                    }
                    line_supplier_ids.append(res)
                    no += 1

        return line_supplier_ids

    def lines(self, company_id, supplier_id):
        lines = []
        data_form = self.localcontext['data']['form']
        date_from = data_form['invoice_date_from']
        date_to = data_form['invoice_date_to']

        obj_move = self.pool.get('account.move')
        obj_move_line = self.pool.get('account.move.line')
        obj_period = self.pool.get('account.period')

        period_id = obj_period.find(self.cr, self.uid, date_from)

        kriteria_move = [
            ('company_id', '=', company_id),
            ('partner_id', '=', supplier_id),
            ('state', '=', 'posted'),
            ('period_id', '=', period_id)
        ]

        move_ids = obj_move.search(self.cr, self.uid, kriteria_move)

        if move_ids:
            for move_id in move_ids:
                if move_id:

                    move_line = [
                                ('move_id', '=', move_id),
                                ('credit', '>', 0),
                                ('account_id.type', '=', 'payable')
                    ]

                    move_line_ids = obj_move_line.search(
                        self.cr, self.uid, move_line
                    )

                    if move_line_ids:
                        for move_line_id in move_line_ids:

                            move_line = obj_move_line.browse(
                                self.cr, self.uid, move_line_id
                            )

                            date_due = move_line.date_maturity

                            if date_from <= date_due and date_to >= date_due:
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
