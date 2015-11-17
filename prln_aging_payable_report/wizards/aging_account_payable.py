# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Michael Viriyananda
#    Copyright 2015 Opensynergy Indonesia
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

from osv import fields, osv

class aging_account_payable_detail_companies(osv.osv_memory):
	_name = 'pralon.aging_account_payable_detail_companies'
	_description = 'Aging Account Payable Detail Companies'
        
	_columns =  {
		'wizard_id' : fields.many2one(string='Wizard ID', obj='pralon.aging_account_payable', required=True),
		'company_id' : fields.many2one(string='Companies', obj='res.company', required=True),
	}

aging_account_payable_detail_companies()
                                
class aging_account_payable_detail_supplier(osv.osv_memory):
	_name = 'pralon.aging_account_payable_detail_supplier'
	_description = 'Aging Account Payable Detail Supplier'

	_columns =  {
		'wizard_id' : fields.many2one(string='Wizard ID', obj='pralon.aging_account_payable', required=True),
		'supplier_id' : fields.many2one(string='Supplier', obj='res.partner', required=True),
	}
                                
aging_account_payable_detail_supplier()

class aging_account_payable(osv.osv_memory):
	_name = 'pralon.aging_account_payable'
	_description = 'Aging Account Payable Report'
        
	_columns =  {
		'company_ids' : fields.one2many(string='Companies', required=True, obj='pralon.aging_account_payable_detail_companies', fields_id='wizard_id'),
		'supplier_ids' : fields.one2many(string='Supplier', required=True, obj='pralon.aging_account_payable_detail_supplier', fields_id='wizard_id'),
		'invoice_date_from' : fields.date(string='Invoice Date From', required=True),
		'invoice_date_to' : fields.date(string='Invoice Date To', required=True),
		'output_format' : fields.selection(string='Output Format', required=True, selection=[('pdf', 'PDF'),('xls', 'XLS')])
	}
                                                        
	def button_print_report(self, cr, uid, ids, data, context=None):
		datas = {}
		output_format = ''

		if context is None:
			context = {}

		datas['form'] = self.read(cr, uid, ids)[0]

		if datas['form']['invoice_date_from'] > datas['form']['invoice_date_to']:
			raise osv.except_osv('Warning','Invoice Date From cannot be greater than Invoice Date To !')
			
		if datas['form']['company_ids'] == []:
			raise osv.except_osv('Warning','Companies cannot be empty !')
		if datas['form']['supplier_ids'] == []:
			raise osv.except_osv('Warning','Supplier cannot be empty !')
			
		if datas['form']['output_format'] == 'xls':
			output_format = 'report_aging_account_payable_xls'
		elif datas['form']['output_format'] == 'pdf':
			output_format = 'report_aging_account_payable_pdf'
		else:
			raise osv.except_osv('Warning','Output Format cannot be empty !')
				      
		return {
				'type': 'ir.actions.report.xml',
				'report_name': output_format,
				'datas': datas,
		}
                
aging_account_payable()
