# -*- coding: utf-8 -*-
# © 2015 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
                ('xls', 'XLS')
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

        if datas['form']['output_format'] == 'xls':
            output_format = 'report_purchasing_xls'
        elif datas['form']['output_format'] == 'pdf':
            output_format = 'report_purchasing_pdf'
        else:
            err = 'Output Format cannot be empty'
            raise osv.except_osv(_('Warning'), _(err))

        return {
            'type': 'ir.actions.report.xml',
            'report_name': output_format,
            'datas': datas,
        }

purchasing()
