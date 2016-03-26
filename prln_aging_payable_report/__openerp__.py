# -*- coding: utf-8 -*-
# © 2015 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Pralon Aging Payable Account Report Module',
    'version': '1.0.0',
    'author': "Michael Viriyananda,OpenSynergy Indonesia",
    'license': 'AGPL-3',
    'category': 'Reporting',
    'depends': [
        'account',
        'pralon_accounting_reports',
        'report_aeroo_ooo'
    ],
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
    - Accounting->Reporting->Daftar Aging Account Payable

    """,
    'website': 'http://opensynergy-indonesia.com',
    'data': [
        'security/ir.model.access.csv',
        'wizards/aging_account_payable.xml',
        'report/report.xml',
        'menu_Accounting.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True
}
