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


class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.lst_lines = []
        self.report_subtotal = 0.0
        self.report_grandtotal = 0.0
        self.localcontext.update({
            'time': time,
            'get_po_date_from': self.get_po_date_from,
            'get_po_date_to': self.get_po_date_to,
            'get_companies': self.get_companies,
            'get_department': self.get_department,
            'get_pricelist': self.get_pricelist,
            'get_subtotal': self.get_report_subtotal,
            'get_total': self.get_report_total,
            'grand_total': self.get_report_grandtotal,
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

        line_ids = obj_purchase_line.search(self.cr, self.uid, kriteria)

        if line_ids:
            line = obj_purchase_line.browse(self.cr, self.uid, line_ids)[0]
            sub_total = line.price_subtotal

        return sub_total

    def get_ppn(self, line_id):
        ppn = 'x'

        obj_user = self.pool.get('res.users')
        user = obj_user.browse(self.cr, self.uid, [self.uid])[0]

        tax_ids = user.company_id.tax_ids

        if tax_ids:
            self.cr.execute("""\
                SELECT  ord_id AS ord_id,
                        tax_id AS tax_id
                FROM    purchase_order_taxe
                WHERE   ord_id=%s AND
                        tax_id IN %s
                """, (line_id, tuple(user.company_id.tax_ids)))
            if self.cr.dictfetchall():
                ppn = 'v'

        return ppn

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

    def get_pricelist(self):
        line_pricelist_ids = []

        self.cr.execute("""\
            SELECT DISTINCT pricelist_id AS pricelist_id,
                        pricelist_name AS pricelist_name
            FROM        pralon_query_purchasing_report
            """)
        for pricelist in self.cr.dictfetchall():
            res = {
                'name': pricelist['pricelist_name'],
                'id': pricelist['pricelist_id']
            }
            line_pricelist_ids.append(res)

        return line_pricelist_ids

    def get_department(self):
        line_department_ids = []

        obj_department = self.pool.get('hr.department')
        data_form = self.localcontext['data']['form']
        data_department_ids = data_form['department_ids']

        if data_department_ids:
            kriteria = [('id', '=', data_department_ids)]
            department_ids = obj_department.search(self.cr, self.uid, kriteria)
            for department_id in department_ids:
                if department_id:
                    department = obj_department.browse(
                        self.cr, self.uid, department_id
                    )
                    res = {
                        'name': department.name,
                        'id': department.id
                    }
                    line_department_ids.append(res)
        return line_department_ids

    def get_report_subtotal(self, amount):
        self.report_subtotal += amount
        return True

    def get_report_total(self):
        total = 0.0
        total = self.report_subtotal
        self.report_subtotal = 0.0
        self.report_grandtotal += total

        return total

    def get_report_grandtotal(self):
        grand_total = 0.0
        grand_total = self.report_grandtotal
        self.report_grandtotal = 0.0
        return grand_total

    def lines(self):
        dict_data = {}

        data_form = self.localcontext['data']['form']
        date_from = data_form['po_date_from']
        date_to = data_form['po_date_to']

        obj_line = self.pool.get('pralon.query_purchasing_report')

        kriteria = [
            ('date_approve', '>=', date_from),
            ('date_approve', '<=', date_to)
        ]

        line_ids = obj_line.search(self.cr, self.uid, kriteria)

        if line_ids:
            line_id = obj_line.browse(self.cr, self.uid, line_ids)
            for line in line_id:
                company_id = line.company_id.id
                company_name = line.company_id.name
                pricelist_id = line.pricelist_id.id
                pricelist_name = line.pricelist_id.name
                department_id = line.department_id.id

                if not dict_data.get(company_id, False):
                    dict_company = {
                        'company_id': company_id,
                        'company_name': company_name,
                        'pricelist_ids': {}
                    }
                    dict_data[company_id] = dict_company

                data_company = dict_data[company_id]

                data_pricelist_ids = data_company['pricelist_ids']

                if not data_pricelist_ids.get(
                    pricelist_id, False
                ):
                    dict_pricelist = {
                        'pricelist_id': pricelist_id,
                        'pricelist_name': pricelist_name,
                        'department_ids': {}
                    }
                    data_pricelist_ids[pricelist_id] = dict_pricelist

                data_pricelist = data_pricelist_ids[pricelist_id]

                data_department = data_pricelist['department_ids']

                if not data_department.get(
                    department_id, False
                ):
                    dict_department = {
                        'department_id': department_id,
                        'lines': []
                    }
                    data_department[department_id] = dict_department

                dict_lines = {
                    'department': line.department_id.name,
                    'pr_no': line.requisition_id.name,
                    'pr_date': line.requisition_id.date_start,
                    'product': line.product_id.name_template,
                    'supplier': line.partner_id.name,
                    'po_no': line.order_id.name,
                    'po_date': line.order_id.date_order,
                    'po_qty': line.po_qty,
                    'unit_price': line.unit_price,
                    'ppn': self.get_ppn(line.id),
                    'total': self.get_subtotal(line.id),
                    'is_no': line.picking_id.name,
                    'is_date': line.picking_id.date_done,
                    'is_qty': line.move_id.product_qty,
                    'warehouse': line.warehouse_id.name

                }
                data_lines = data_department[department_id]['lines']
                data_lines.append(dict_lines)

        return dict_data
