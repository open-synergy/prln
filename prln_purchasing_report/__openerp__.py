# -*- coding: utf-8 -*-
# © 2015 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Pralon Purchasing Report Module',
    'version': '1.0.0',
    'author': "Michael Viriyananda,OpenSynergy Indonesia",
    'license': 'AGPL-3',
    'category': 'Reporting',
    'depends': [
        'purchase',
        'purchase_requisition',
        'pralon_purchase_enhancements',
        'report_aeroo_ooo',
        'pralon_accounting_reports',
        'via_purchase_enhancements',
        'pralon_sale_enhancements'
    ],
    'description': """
Purchasing Report Based On Purchase Order.
============================

Creates a purchasing report for accountants based using aeroo
--------------------------------------------------
* Wizard with parameter:
    - Companies
    - Departments
    - PO Date From
    - PO Date To
    - Output Format(PDF/XLS/CSV)

    """,
    'website': 'http://opensynergy-indonesia.com',
    'data': [
        'security/ir.model.access.csv',
        'wizards/purchasing.xml',
        'view/view_ResCompany.xml',
        'report/report.xml',
        'menu_Accounting.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True
}
