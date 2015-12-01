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
from tools.translate import _


class purchasing(osv.osv_memory):
    _name = 'pralon.purchasing'
    _description = 'Purchasing Report Based On Purchase Order'

    _columns = {
        'company_ids': fields.many2many(
            obj='res.company',
            rel='purchasing_company_rel',
            id1='wizard_id',
            id2='company_id',
            string='Companies'
        ),
        'department_ids': fields.many2many(
            obj='hr.department',
            rel='purchasing_supplier_rel',
            id1='wizard_id',
            id2='department_id',
            string='Departments'
        ),
        'po_date_from': fields.date(
            string='PO Date From',
            required=True
        ),
        'po_date_to': fields.date(
            string='PO Date To',
            required=True
        ),
        'output_format': fields.selection(
            string='Output Format',
            required=True,
            selection=[
                ('pdf', 'PDF'),
                ('xls', 'XLS'),
                ('csv', 'CSV')
            ]
        )
    }

    def button_print_report(self, cr, uid, ids, data, context=None):
        datas = {}
        output_format = ''

        if context is None:
            context = {}

        datas['form'] = self.read(cr, uid, ids)[0]

        po_date_from = datas['form']['po_date_from']
        po_date_to = datas['form']['po_date_to']

        if po_date_from > po_date_to:
            err = 'PO Date From cannot be greater than PO Date To !'
            raise osv.except_osv(_('Warning'), _(err))

        if datas['form']['company_ids'] == []:
            err = 'Companies cannot be empty'
            raise osv.except_osv(_('Warning'), _(err))
            err = 'Department cannot be empty'
        if datas['form']['department_ids'] == []:
            raise osv.except_osv(_('Warning'), _(err))

        if datas['form']['output_format'] == 'xls':
            output_format = 'report_purchasing_xls'
        elif datas['form']['output_format'] == 'pdf':
            output_format = 'report_purchasing_pdf'
        elif datas['form']['output_format'] == 'csv':
            output_format = ''
        else:
            err = 'Output Format cannot be empty'
            raise osv.except_osv(_('Warning'), _(err))

        return {
            'type': 'ir.actions.report.xml',
            'report_name': output_format,
            'datas': datas,
        }

purchasing()
