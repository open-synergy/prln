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
from openerp.tools.translate import _
from openerp.osv import fields, osv


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
                        self.cr, self.uid, department_id
                    )
                    res = {
                        'name': department.name,
                        'id': department.id
                    }
                    line_department_ids.append(res)

        return line_department_ids

    def lines(self):
        lst_companies = []
        lst_pricelist = []
        lst_department = []
        res_companies = []
        res_pricelist = []
        res_department = []
        
        obj_line = self.pool.get('pralon.query_purchasing_report')
        
        kriteria = []
        
        line_ids = obj_line.search(self.cr, self.uid, kriteria)
        
        if line_ids:
            line_id = obj_line.browse(self.cr, self.uid, line_ids)
            for line in line_id:

                company_id = line.company_id.id
                company_name = line.company_id.name
                pricelist_id = line.pricelist_id.id
                pricelist_name = line.pricelist_id.name
                department_id = line.department_id.id
                
                res_lines = []
                
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
                    'is_no': line.picking_id.name,
                    'is_date': line.picking_id.date_done,
                    'is_qty': line.move_id.product_qty,
                    'warehouse': line.warehouse_id.name
                }
                res_lines.append(dict_lines)
                
                if department_id in lst_department:
                    for chk_department in res_department:
                        if chk_department['department_id'] == department_id:
                            chk_department['lines'].append(dict_lines)
                            break
                                
                else:
                    dict_department = {
                        'department_id': department_id,
                        'lines': res_lines
                    }
                    res_department.append(dict_department)
                    lst_department.append(department_id)
                
                if pricelist_id in lst_pricelist:
                    for chk_pricelist in res_pricelist:
                    
                        data_pricelist = chk_pricelist['pricelist_id']
                        data_p_department = chk_pricelist['department_ids']
                        
                        if data_pricelist == pricelist_id:
                        
                            for data_p in data_p_department:
                            
                                if data_p['department_id'] == department_id:
                                
                                    chk_pricelist['department_ids'].append(dict_department)
                                    break
                else:
                    dict_pricelist = {
                        'pricelist_id': pricelist_id,
                        'pricelist_name': pricelist_name,
                        'department_ids': res_department
                    }
                    res_pricelist.append(dict_pricelist)
                    lst_pricelist.append(pricelist_id)
                    
                if company_id in lst_companies:
                    for chk_company in self.lst_lines:
                    
                        data_company = chk_company['company_id']
                        data_c_pricelist = chk_company['pricelist_ids']
                        
                        if data_company == company_id:
                        
                            for data_c in data_c_pricelist:

                                if data_c['pricelist_id'] == pricelist_id:
                                
                                    for data_cd in data_c['department_ids']:
                                
                                        if data_cd['department_id'] == department_id:
                                            data_cd['lines'].append(dict_lines)
                                        else:
                                            dict_companies = {
                                                'company_id': company_id,
                                                'company_name': company_name,
                                                'pricelist_ids':res_pricelist
                                            }
                                            self.lst_lines.append(dict_companies)
                                            lst_companies.append(company_id)
                                            
                                else:
                                    dict_pricelist = {
                                        'pricelist_id': pricelist_id,
                                        'pricelist_name': pricelist_name,
                                        'department_ids': res_department
                                    }
                                    res_pricelist.append(dict_pricelist)
                                    lst_pricelist.append(pricelist_id)
                        else:
                            dict_companies = {
                                'company_id': company_id,
                                'company_name': company_name,
                                'pricelist_ids':[]
                            }
                                    
                else:
                    dict_companies = {
                        'company_id': company_id,
                        'company_name': company_name,
                        'pricelist_ids':res_pricelist
                    }
                    self.lst_lines.append(dict_companies)
                    lst_companies.append(company_id)
                
        raise osv.except_osv(_('BUGS!'), _("'%s'") % (self.lst_lines))
        return self.lst_lines
