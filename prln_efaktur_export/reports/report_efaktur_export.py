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
from report import report_sxw


class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.lines = []
        self.localcontext.update({'get_lines':self.get_lines})

    def get_lines(self):
        pool = self.pool
        cr = self.cr
        uid = self.uid
        obj_taxform = pool.get('account.taxform')
        taxform_ids = self.localcontext.get('active_ids')
        if not taxform_ids:
            return self.lines

        for o in obj_taxform.browse(cr, uid, taxform_ids):
            data = {
                'taxform_id': o.taxform_id,
                }

            self.lines.append(data)
        return self.lines
