# -*- coding: utf-8 -*-
# © 2015 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from osv import osv


class wzd_efaktur_export(osv.osv_memory):
    _name = 'pralon.wzd_efaktur_export'
    _description = 'Export To eFaktur'

    def button_print_report(self, cr, uid, ids, context=None):
        datas = {}

        if context is None:
            context = {}

        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'taxform_ids':  context.get('active_ids', [])})

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_pralon_efakturExport_csv',
            'datas': datas,
        }
wzd_efaktur_export()
