# -*- coding: utf-8 -*-
# © 2015 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'eFaktur Export',
    'version': '1.0.0',
    'author': "Andhitia Rama,OpenSynergy Indonesia",
    'license': 'AGPL-3',
    'category': 'Reporting',
    'depends': [
        'prln_taxform_vat_rounding',
        'pralon_accounting_reports',
        'report_aeroo_ooo'
    ],
    'description': """
    """,
    'website': 'http://opensynergy-indonesia.com',
    'data': [
        'views/res_partner_views.xml',
        'wizards/wzd_efaktur_export.xml',
        'reports/report_efaktur_export_csv.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True
}
