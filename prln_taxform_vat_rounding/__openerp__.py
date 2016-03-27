# -*- coding: utf-8 -*-
# © 2015 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Taxform VAT Rounding',
    'version': '1.0.0',
    'author': "Andhitia Rama,OpenSynergy Indonesia",
    'license': 'AGPL-3',
    'category': 'Sale',
    'depends': [
        'via_account_taxform',
        'prln_invoice_vat_rounding',
    ],
    'description': """
    """,
    'website': 'http://opensynergy-indonesia.com',
    'data': [
        'views/account_taxform_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True
}
