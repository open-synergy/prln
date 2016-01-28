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
from datetime import datetime
from report import report_sxw


class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.lst_lines = []
        self.lst_currency = []
        self.line_currency_ids = []
        self.report_subtotal = 0.0
        self.report_grandtotal = 0.0
        self.localcontext.update({
            'time': time,
            'get_po_date_from': self.get_po_date_from,
            'get_po_date_to': self.get_po_date_to,
            'get_companies': self.get_companies,
            'get_department': self.get_department,
            'get_currency': self.get_currency,
            'get_lines_id': self.get_lines_id,
            'get_subtotal': self.get_report_subtotal,
            'get_total': self.get_report_total,
            'grand_total': self.get_report_grandtotal,
            'get_po_pr': self.get_po_pr,
            'get_list_currency': self.get_list_currency,
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

    def get_po_date_from(self):
        po_date_from = self.localcontext['data']['form']['po_date_from']
        convert_date_from = self.convert_date(po_date_from)
        return convert_date_from

    def get_po_date_to(self):
        po_date_to = self.localcontext['data']['form']['po_date_to']
        convert_date_to = self.convert_date(po_date_to)

        return convert_date_to

    def get_subtotal(self, line_id):
        sub_total = 0.0
        obj_purchase_line = self.pool.get('purchase.order.line')

        kriteria = [
            ('id', '=', line_id)
        ]

        line_ids = obj_purchase_line.search(self.cr, self.uid, kriteria)[0]

        if line_ids:
            line = obj_purchase_line.browse(self.cr, self.uid, line_ids)
            sub_total = line.price_subtotal

        return sub_total

    def get_ppn(self, line_id):
        lst_tax = []
        ppn = 'x'

        obj_user = self.pool.get('res.users')
        user = obj_user.browse(self.cr, self.uid, [self.uid])[0]

        for tax in user.company_id.tax_ids:
            if tax.id:
                lst_tax.append(tax.id)

        if lst_tax:
            self.cr.execute("""\
                SELECT  ord_id AS ord_id,
                        tax_id AS tax_id
                FROM    purchase_order_taxe
                WHERE   ord_id=%s AND
                        tax_id IN %s
                """, (line_id, tuple(lst_tax),))
            if self.cr.dictfetchall():
                ppn = 'v'

        return ppn

    def get_companies(self):
        line_companies_ids = []
        company = []

        obj_company = self.pool.get('res.company')
        obj_query = self.pool.get('pralon.query_purchasing_report')

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

                    kriteria_query = [
                        ('company_id', '=', company.id)
                    ]

                    query_ids = obj_query.search(
                        self.cr, self.uid, kriteria_query
                    )

                    if query_ids:

                        res = {
                            'name': company.name,
                            'id': company.id
                        }
                        line_companies_ids.append(res)

        return line_companies_ids

    def get_currency(self):
        data_form = self.localcontext['data']['form']
        date_from = data_form['po_date_from']
        date_to = data_form['po_date_to']
        list_department = []
        list_company = []

        for department in self.get_department():
            list_department.append(department['id'])

        for company in self.get_companies():
            list_company.append(company['id'])

        self.cr.execute("""\
            SELECT DISTINCT currency_id AS currency_id,
                        currency_name AS currency_name
            FROM    pralon_query_purchasing_report
            WHERE   date_approve >= %s AND
                    date_approve <= %s AND
                    company_id in %s AND
                    department_id in %s
            """, (
            date_from,
            date_to,
            tuple(list_company),
            tuple(list_department))
        )

        for currency in self.cr.dictfetchall():
            if currency:
                res = {
                    'name': currency['currency_name'],
                    'id': currency['currency_id']
                }
                self.line_currency_ids.append(res)

        return self.line_currency_ids

    def get_lines_id(self):
        line_ids = []
        data_form = self.localcontext['data']['form']
        date_from = data_form['po_date_from']
        date_to = data_form['po_date_to']
        list_department = []
        list_company = []

        for department in self.get_department():
            list_department.append(department['id'])

        for company in self.get_companies():
            list_company.append(company['id'])

        self.cr.execute("""\
            SELECT DISTINCT line_id AS line_id
            FROM    pralon_query_purchasing_report
            WHERE   date_approve >= %s AND
                    date_approve <= %s AND
                    company_id in %s AND
                    department_id in %s
            ORDER BY line_id
            """, (
            date_from,
            date_to,
            tuple(list_company),
            tuple(list_department))
        )

        for lines in self.cr.dictfetchall():
            res = {
                'id': lines['line_id']
            }
            line_ids.append(res)

        return line_ids

    def get_department(self):
        line_department_ids = []
        department = []

        obj_department = self.pool.get('hr.department')
        obj_query = self.pool.get('pralon.query_purchasing_report')

        data_form = self.localcontext['data']['form']
        data_department_ids = data_form['department_ids']

        if data_department_ids:
            kriteria = [('id', '=', data_department_ids)]
        else:
            kriteria = []

        department_ids = obj_department.search(self.cr, self.uid, kriteria)

        if department_ids:

            for department_id in department_ids:

                if department_id:
                    department = obj_department.browse(
                        self.cr, self.uid, department_id
                    )

                    kriteria_query = [
                        ('department_id', '=', department.id)
                    ]

                    query_ids = obj_query.search(
                        self.cr, self.uid, kriteria_query
                    )

                    if query_ids:
                        res = {
                            'name': department.name,
                            'id': department.id
                        }
                        line_department_ids.append(res)

        return line_department_ids

    def get_po_pr(self, status):
        data_form = self.localcontext['data']['form']
        date_from = data_form['po_date_from']
        date_to = data_form['po_date_to']
        list_department = []
        list_company = []

        for department in self.get_department():
            list_department.append(department['id'])

        for company in self.get_companies():
            list_company.append(company['id'])

        self.cr.execute("""\
            SELECT  COUNT(DISTINCT order_id) AS total_po,
                    COUNT(DISTINCT requisition_id) AS total_pr
            FROM    pralon_query_purchasing_report
            WHERE   date_approve >= %s AND
                    date_approve <= %s AND
                    company_id in %s AND
                    department_id in %s
            """, (
            date_from,
            date_to,
            tuple(list_company),
            tuple(list_department))
        )

        for lines in self.cr.dictfetchall():
            if status == 'po':
                return lines['total_po']
            if status == 'pr':
                return lines['total_pr']

    def get_report_subtotal(self, amount, status):
        if status == 'line':
            self.report_subtotal += amount
        return True

    def get_report_total(self, currency_name):
        res = {}
        total = 0.0
        total = self.report_subtotal
        self.report_subtotal = 0.0
        self.report_grandtotal += total

        res = {
            'currency_name': currency_name,
            'total': total
        }
        self.lst_currency.append(res)

        return total

    def get_report_grandtotal(self):
        grand_total = self.report_grandtotal
        self.report_grandtotal = 0.0

        return grand_total

    def get_list_currency(self):
        summary = []
        for data in self.line_currency_ids:
            total = 0
            currency_name = data['name']

            if not data:
                return False

            for x in self.lst_currency:
                if not x:
                    return False

                if x['currency_name'] == currency_name:
                    total += x['total']
            res = {
                'currency_name': currency_name,
                'total': total
            }
            summary.append(res)
        return summary

    def lines(self):
        dict_data = {}
        count_data = 0
        po_is = 0.0

        data_form = self.localcontext['data']['form']
        date_from = data_form['po_date_from']
        date_to = data_form['po_date_to']

        obj_line = self.pool.get('pralon.query_purchasing_report')

        kriteria = [
            ('date_approve', '>=', date_from),
            ('date_approve', '<=', date_to)
        ]

        line_ids = obj_line.search(
            self.cr, self.uid, kriteria, order='pr_no desc')

        if line_ids:
            line_id = obj_line.browse(self.cr, self.uid, line_ids)
            for line in line_id:
                company_id = line.company_id.id
                company_name = line.company_id.name
                currency_id = line.currency_id.id
                currency_name = line.currency_name
                department_id = line.department_id.id
                department_name = line.department_id.name
                lines_id = line.line_id.id

                if not dict_data.get(company_id, False):
                    dict_company = {
                        'company_id': company_id,
                        'company_name': company_name,
                        'currency_ids': {}
                    }
                    dict_data[company_id] = dict_company

                data_company = dict_data[company_id]

                data_currency_ids = data_company['currency_ids']

                if not data_currency_ids.get(
                    currency_id, False
                ):
                    dict_currency = {
                        'currency_id': currency_id,
                        'currency_name': currency_name,
                        'department_ids': {}
                    }
                    data_currency_ids[currency_id] = dict_currency

                data_currency = data_currency_ids[currency_id]

                data_department = data_currency['department_ids']

                if not data_department.get(
                    department_id, False
                ):
                    dict_department = {
                        'department_id': department_id,
                        'department_name': department_name,
                        'shipment_ids': {}
                    }
                    data_department[department_id] = dict_department

                data_department = data_department[department_id]

                data_shipment = data_department['shipment_ids']

                if not data_shipment.get(
                    lines_id, False
                ):
                    dict_shipment = {
                        'lines_id': lines_id,
                        'lines': []
                    }
                    data_shipment[lines_id] = dict_shipment
                    count_data = 0
                    po_is = line.po_qty

                pr_date = line.requisition_id.date_start
                conv_pr_date = datetime.strptime(
                    pr_date, '%Y-%m-%d %H:%M:%S').strftime(
                        '%d/%m/%Y %H:%M:%S')

                po_date = line.order_id.date_order
                conv_po_date = datetime.strptime(
                    po_date, '%Y-%m-%d').strftime('%d/%m/%Y')

                is_date = line.picking_id.date_done
                conv_is_date = datetime.strptime(
                    is_date, '%Y-%m-%d %H:%M:%S').strftime(
                        '%d/%m/%Y')

                if count_data == 0:
                    po_is -= line.is_qty
                    dict_lines = {
                        'department': line.department_id.name,
                        'pr_no': line.pr_no,
                        'pr_date': conv_pr_date,
                        'product': line.product_id.name_template[:30],
                        'supplier': line.partner_id.name,
                        'po_no': line.order_id.order_number,
                        'po_date': conv_po_date,
                        'po_qty': line.po_qty,
                        'uom_name': line.uom_name,
                        'po_is': po_is,
                        'unit_price': line.unit_price,
                        'symbol': line.symbol,
                        'ppn': self.get_ppn(line.id),
                        'total': self.get_subtotal(line.line_id.id),
                        'is_no': line.picking_id.name,
                        'is_date': conv_is_date,
                        'is_qty': line.is_qty,
                        'is_uom_name': line.is_uom_name,
                        'warehouse': line.warehouse_id.code,
                        'status': 'line'
                    }
                    count_data += 1
                else:
                    po_is -= line.is_qty
                    dict_lines = {
                        'department': line.department_id.name,
                        'pr_no': line.pr_no,
                        'pr_date': conv_pr_date,
                        'product': line.product_id.name_template[:30],
                        'supplier': line.partner_id.name,
                        'po_no': line.order_id.order_number,
                        'po_date': conv_po_date,
                        'po_qty': line.po_qty,
                        'uom_name': line.uom_name,
                        'po_is': po_is,
                        'unit_price': line.unit_price,
                        'symbol': line.symbol,
                        'ppn': self.get_ppn(line.id),
                        'total': self.get_subtotal(line.line_id.id),
                        'is_no': line.picking_id.name,
                        'is_date': conv_is_date,
                        'is_qty': line.is_qty,
                        'is_uom_name': line.is_uom_name,
                        'warehouse': line.warehouse_id.code,
                        'status': 'detail'
                    }
                data_lines = data_shipment[lines_id]['lines']
                data_lines.append(dict_lines)
        return dict_data
