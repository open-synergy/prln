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
    'name': 'Pralon Aging Payable Account Report Module',
    'version': '1.0.0',
    'author': "Michael Viriyananda,OpenSynergy Indonesia",
    'license': 'AGPL-3',
    'category': 'Reporting',
    'depends': ['account', 'report_aeroo_ooo'],
    'description': """
Aging Payable Account Report.
============================

Creates a aging payable account report for accountants based using aeroo
--------------------------------------------------
* Wizard with parameter:
    - Companies
    - Supplier
    - Invoice Date From
    - Invoice Date To
    - Output Format(PDF/XLS)

* Menu
    - Accounting -> Reporting -> Daftar Aging Account Payable 

    """,
    'website': 'http://opensynergy-indonesia.com',
    'data': [
        'wizards/aging_account_payable.xml',
        'report/report.xml',
        'menu_Accounting.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True
}
