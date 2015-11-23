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

from datetime import datetime, date, time
import time
from report import report_sxw


class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_po_date_from': self.get_po_date_from,
            'get_po_date_to': self.get_po_date_to,
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
