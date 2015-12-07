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

import time
from report import report_sxw
from datetime import datetime


class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.lst_lines = []
        self.localcontext.update({
            'time': time,
            'get_invoice_date_from': self.get_invoice_date_from,
            'get_invoice_date_to': self.get_invoice_date_to,
            'get_date_as_of': self.get_date_as_of,
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
        convert_date_from = '-'
        data_form = self.localcontext['data']['form']
        invoice_date_from = data_form['invoice_date_from']
        if invoice_date_from:
            convert_date_from = self.convert_date(invoice_date_from)
        return convert_date_from

    def get_invoice_date_to(self):
        convert_date_to = '-'
        data_form = self.localcontext['data']['form']
        invoice_date_to = data_form['invoice_date_to']
        if invoice_date_to:
            convert_date_to = self.convert_date(invoice_date_to)
        return convert_date_to

    def get_date_as_of(self):
        convert_date_as_of = '-'
        data_form = self.localcontext['data']['form']
        date_as_of = data_form['date_as_of']
        if date_as_of:
            convert_date_as_of = self.convert_date(date_as_of)
        return convert_date_as_of

    def get_companies(self):
        line_companies_ids = []

        obj_company = self.pool.get('res.company')
        data_form = self.localcontext['data']['form']
        data_company_ids = data_form['company_ids']

        if data_company_ids:
            kriteria = [('id', '=', data_company_ids)]
        else:
            kriteria = []

        company_ids = obj_company.search(self.cr, self.uid, kriteria)

        if company_ids:
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
        else:
            kriteria = []

        supplier_ids = obj_supplier.search(self.cr, self.uid, kriteria)

        if supplier_ids:
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

    def get_residual(self, move_line_ids, date_as_of):
        residual = 0.0
        obj_move_line = self.pool.get('account.move.line')

        move_line = obj_move_line.browse(
            self.cr, self.uid, move_line_ids
        )[0]

        partial_ids = move_line.reconcile_partial_id.line_partial_ids

        if move_line.reconcile_partial_id:
            for payment_line in partial_ids:
                if payment_line.date <= date_as_of:
                    residual += (payment_line.debit - payment_line.credit)
        else:
            residual = move_line.amount_residual

        return abs(residual)

    def lines(self):
        data_form = self.localcontext['data']['form']
        date_from = data_form['invoice_date_from']
        date_to = data_form['invoice_date_to']
        date_as_of = data_form['date_as_of']

        obj_move = self.pool.get('account.move')
        obj_move_line = self.pool.get('account.move.line')

        ord_date = datetime.strptime(date_as_of, '%Y-%m-%d').toordinal()

        # GET LIST COMPANIES
        for company in self.get_companies():
            t_acc_payable = 0.0
            t_curr = 0.0
            t_aging1 = 0.0
            t_aging2 = 0.0
            t_aging3 = 0.0
            t_aging4 = 0.0

            dict_companies = {
                'company_id': company['id'],
                'company_name': company['name'],
                'supplier_ids': []
            }

            # GET LIST SUPPLIERS
            for supplier in self.get_supplier():
                res_line = []
                st_acc_payable = 0.0
                st_curr = 0.0
                st_aging1 = 0.0
                st_aging2 = 0.0
                st_aging3 = 0.0
                st_aging4 = 0.0

                # GET LINES

                if date_from and not date_to:
                    kriteria_move = [
                        ('company_id', '=', company['id']),
                        ('partner_id', '=', supplier['id']),
                        ('state', '=', 'posted'),
                        ('date', '>=', date_from)
                    ]

                if not date_from and date_to:
                    kriteria_move = [
                        ('company_id', '=', company['id']),
                        ('partner_id', '=', supplier['id']),
                        ('state', '=', 'posted'),
                        ('date', '<=', date_to)
                    ]

                if date_from and date_to:
                    kriteria_move = [
                        ('company_id', '=', company['id']),
                        ('partner_id', '=', supplier['id']),
                        ('state', '=', 'posted'),
                        ('date', '>=', date_from),
                        ('date', '<=', date_to)
                    ]

                if not date_from and not date_to:
                    kriteria_move = [
                        ('company_id', '=', company['id']),
                        ('partner_id', '=', supplier['id']),
                        ('state', '=', 'posted')
                    ]

                move_ids = obj_move.search(
                    self.cr, self.uid, kriteria_move, order='name asc'
                )

                if move_ids:
                    for move_id in move_ids:
                        if move_id:

                            move_line = [
                                ('move_id', '=', move_id),
                                ('credit', '>', 0),
                                ('account_id.type', '=', 'payable')
                            ]

                            move_line_ids = obj_move_line.search(
                                self.cr, self.uid, move_line, order='name asc'
                            )

                            if move_line_ids:
                                move_line = obj_move_line.browse(
                                    self.cr, self.uid, move_line_ids
                                )[0]

                                if move_line.reconcile_id:
                                    continue

                                date_due = move_line.date_maturity
                                residual = self.get_residual(
                                    move_line_ids, date_as_of
                                )
                                acc_payable = move_line.credit
                                name = move_line.move_id.name

                                if date_due:
                                    ord_date_due = datetime.strptime(
                                        date_due, '%Y-%m-%d').toordinal()
                                    overdue = ord_date_due - ord_date

                                    # NOTE
                                    # aging1 : overdue 1-30
                                    # aging2 : overdue 31-60
                                    # aging3 : overdue 61-90
                                    # aging4 : overdue >=90

                                    if overdue >= 0:
                                        res = {
                                            'name': name,
                                            'acc_payable': acc_payable,
                                            'current': residual,
                                            'aging1': False,
                                            'aging2': False,
                                            'aging3': False,
                                            'aging4': False
                                        }
                                        st_acc_payable += acc_payable
                                        st_curr += residual

                                    if overdue <= 0:
                                        overdue = abs(overdue)

                                        if overdue >= 1 and overdue <= 30:
                                            res = {
                                                'name': name,
                                                'acc_payable': acc_payable,
                                                'current': False,
                                                'aging1': residual,
                                                'aging2': False,
                                                'aging3': False,
                                                'aging4': False
                                            }
                                            st_acc_payable += acc_payable
                                            st_aging1 += residual

                                        if overdue >= 31 and overdue <= 60:
                                            res = {
                                                'name': name,
                                                'acc_payable': acc_payable,
                                                'current': False,
                                                'aging1': False,
                                                'aging2': residual,
                                                'aging3': False,
                                                'aging4': False
                                            }
                                            st_acc_payable += acc_payable
                                            st_aging2 += residual

                                        if overdue >= 61 and overdue <= 90:
                                            res = {
                                                'name': name,
                                                'acc_payable': acc_payable,
                                                'current': False,
                                                'aging1': False,
                                                'aging2': False,
                                                'aging3': residual,
                                                'aging4': False
                                            }
                                            st_acc_payable += acc_payable
                                            st_aging3 += residual

                                        if overdue >= 90:
                                            res = {
                                                'name': name,
                                                'acc_payable': acc_payable,
                                                'current': False,
                                                'aging1': False,
                                                'aging2': False,
                                                'aging3': False,
                                                'aging4': residual
                                            }
                                            st_acc_payable += acc_payable
                                            st_aging4 += residual
                                    res_line.append(res)

                    if res_line:
                        dict_supplier = {
                            'no': supplier['no'],
                            'supplier_id': supplier['id'],
                            'supplier_name': supplier['name'],
                            'lines': res_line
                        }

                        dict_supplier['st_acc_payable'] = st_acc_payable
                        dict_supplier['st_curr'] = st_curr
                        dict_supplier['st_aging1'] = st_aging1
                        dict_supplier['st_aging2'] = st_aging2
                        dict_supplier['st_aging3'] = st_aging3
                        dict_supplier['st_aging4'] = st_aging4

                        dict_companies['supplier_ids'].append(dict_supplier)

                    t_acc_payable += st_acc_payable
                    t_curr += st_curr
                    t_aging1 += st_aging1
                    t_aging2 += st_aging2
                    t_aging3 += st_aging3
                    t_aging4 += st_aging4

            dict_companies['t_acc_payable'] = t_acc_payable
            dict_companies['t_curr'] = t_curr
            dict_companies['t_aging1'] = t_aging1
            dict_companies['t_aging2'] = t_aging2
            dict_companies['t_aging3'] = t_aging3
            dict_companies['t_aging4'] = t_aging4
        self.lst_lines.append(dict_companies)
        return self.lst_lines
