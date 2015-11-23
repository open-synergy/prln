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

from osv import fields, osv


class purchasing_detail_companies(osv.osv_memory):
    _name = 'pralon.purchasing_detail_companies'
    _description = 'Purchasing Detail Companies'

    _columns = {
        'wizard_id': fields.many2one(string='Wizard ID', obj='pralon.purchasing', required=True),
        'company_id': fields.many2one(string='Companies', obj='res.company', required=True),
    }

purchasing_detail_companies()


class purchasing_detail_departments(osv.osv_memory):
    _name = 'pralon.purchasing_detail_departments'
    _description = 'Purchasing Detail Departments'

    _columns = {
        'wizard_id': fields.many2one(string='Wizard ID', obj='pralon.purchasing', required=True),
        'department_id': fields.many2one(string='Departments', obj='hr.department', required=True),
    }

purchasing_detail_departments()


class purchasing(osv.osv_memory):
    _name = 'pralon.purchasing'
    _description = 'Purchasing Report Based On Purchase Order'

    _columns = {
        'company_ids': fields.one2many(string='Companies', required=True, obj='pralon.purchasing_detail_companies', fields_id='wizard_id'),
        'department_ids': fields.one2many(string='Departments', required=True, obj='pralon.purchasing_detail_departments', fields_id='wizard_id'),
        'po_date_from': fields.date(string='PO Date From', required=True),
        'po_date_to': fields.date(string='PO Date To', required=True),
        'output_format': fields.selection(string='Output Format', required=True, selection=[('pdf', 'PDF'), ('xls', 'XLS'), ('csv', 'CSV')])
    }

    def button_print_report(self, cr, uid, ids, data, context=None):
        datas = {}
        output_format = ''

        if context is None:
            context = {}

        datas['form'] = self.read(cr, uid, ids)[0]

        if datas['form']['po_date_from'] > datas['form']['po_date_to']:
            raise osv.except_osv('Warning', 'PO Date From cannot be greater than PO Date To !')

        if datas['form']['company_ids'] == []:
            raise osv.except_osv('Warning', 'Companies cannot be empty !')
        if datas['form']['department_ids'] == []:
            raise osv.except_osv('Warning', 'Departments cannot be empty !')

        if datas['form']['output_format'] == 'xls':
            output_format = 'report_purchasing_xls'
        elif datas['form']['output_format'] == 'pdf':
            output_format = 'report_purchasing_pdf'
        elif datas['form']['output_format'] == 'csv':
            output_format = ''
        else:
            raise osv.except_osv('Warning', 'Output Format cannot be empty !')

        return {
                'type': 'ir.actions.report.xml',
                'report_name': output_format,
                'datas': datas,
        }

purchasing()
