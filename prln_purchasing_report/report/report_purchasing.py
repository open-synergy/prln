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
        self.localcontext.update({
            'time': time,
            'get_po_date_from': self.get_po_date_from,
            'get_po_date_to': self.get_po_date_to,
            'get_companies': self.get_companies,
            'get_department': self.get_department,
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
                        self.cr, self.uid, department_id)
                    res = {
                        'name': department.name,
                        'id': department.id
                    }
                    line_department_ids.append(res)

        return line_department_ids
        
    def lines(self):
        data_form = self.localcontext['data']['form']
        date_from = data_form['po_date_from']
        date_to = data_form['po_date_to']

        obj_po = self.pool.get('purchase.order')
        obj_po_line = self.pool.get('purchase.order.line')

        # GET LIST COMPANIES
        for company in self.get_companies():
            dict_companies = {
                'company_id': company['id'],
                'company_name': company['name'],
                'pricelist_ids': []
            }
            
            # GET LIST PRICELIST
            kriteria_po = [
                ('company_id', '=', company['id']),
                ('date_order', '>=', date_from),
                ('date_order', '<=', date_to),
                ('state', '=', 'done')
            ]
            
            po_ids = obj_po.search(self.cr, self.uid, kriteria_po)
            
            if po_ids:
                for po_id in po_ids:
                    if po_id:
                        po = obj_po.browse(self.cr, self.uid, po_id)
                        
                        dict_pricelist = {
                            'pricelist_id': po.pricelist_id.id,
                            'pricelist_name': po.pricelist_id.name,
                            'lines': []
                        }
                        
                        kriteria_po_line = [
                            ('po_id', '=', po_id)
                        ]
                        
                        po_line_ids = obj_po_line.search(self.cr, self.uid, kriteria_po_line)
                        
                        if po_line_ids:
                            for po_line_id in po_line_ids:
                                if po_line_id:
                                    po_line = obj_po_line.browse(self.cr, self.uid, po_line_id)
                                    
                                    dict_lines = {
                                        'department': po.department_id.name
                                    }
                        
        return self.lst_lines
