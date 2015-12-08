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
{
    'name': 'eFaktur Export',
    'version': '1.0.0',
    'author': "Andhitia Rama,OpenSynergy Indonesia",
    'license': 'AGPL-3',
    'category': 'Reporting',
    'depends': [
        'via_account_taxform',
        'pralon_accounting_reports',
        'report_aeroo_ooo'
    ],
    'description': """
    """,
    'website': 'http://opensynergy-indonesia.com',
    'data': [
        'wizards/wzd_efaktur_export.xml',
        'reports/report_efaktur_export_csv.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True
}
