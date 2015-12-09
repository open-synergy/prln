# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Andhitia Rama
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

from osv import osv


class wzd_efaktur_export(osv.osv_memory):
    _name = 'pralon.wzd_efaktur_export'
    _description = 'Export To eFaktur'

    def button_print_report(self, cr, uid, ids, context=None):
        datas = {}

        if context is None:
            context = {}

        datas['form'] = self.read(cr, uid, ids)[0]
        datas['context']['taxform_ids'] = context.get('active_ids', [])

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_pralon_efakturExport_csv',
            'datas': datas,
        }
wzd_efaktur_export()
