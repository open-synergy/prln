# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import tools
from osv import fields,osv
from datetime import datetime


class pralon_query_purchasing_report(osv.osv):

    _name = 'pralon.query_purchasing_report'
    _description = 'Query Purchasing Report'
    _auto = False

    _columns = {
                'id' : fields.integer(string='ID'),
                'order_id' : fields.many2one(string='Purchase', obj='purchase.order'),
                'company_id' : fields.many2one(string='Company', obj='res.company'),
                'pricelist_id' : fields.many2one(string='Pricelist', obj='product.pricelist'),
                'requisition_id' : fields.many2one(string='Requisition', obj='purchase.requisition'),
                'department_id' : fields.many2one(string='Department', obj='hr.department'),
                'product_id' : fields.many2one(string='Product', obj='product.product'),
                'partner_id' : fields.many2one(string='Partner', obj='res.partner'),
                'po_qty' : fields.float(string='Po QTY'),
                'unit_price' : fields.float(string='Price Unit'),
                'picking_id' : fields.many2one(string='Picking', obj='stock.picking'),
                'move_id' : fields.many2one(string='Move', obj='stock.move'),
                'warehouse_id' : fields.many2one(string='Warehouse', obj='stock.warehouse')
                }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'pralon_query_purchasing_report')
        strSQL =    """
                    CREATE OR REPLACE VIEW pralon_query_purchasing_report AS (
                        SELECT	A.id AS id,
	                            B.id AS order_id,
                                B.company_id AS company_id,
	                            B.pricelist_id AS pricelist_id,
	                            B.requisition_id AS requisition_id,
	                            C.department_id AS department_id,
	                            A.product_id AS product_id,
	                            A.partner_id AS partner_id,
	                            A.product_qty AS po_qty,
	                            A.price_unit AS unit_price,
	                            E.id AS picking_id,
	                            D.id AS move_id,
	                            B.warehouse_id AS warehouse_id
                        FROM 	purchase_order_line AS A
                        JOIN	purchase_order AS B ON A.order_id=B.id
                        JOIN	purchase_requisition AS C ON B.requisition_id=C.id
                        JOIN	stock_move AS D ON A.id=D.purchase_line_id
                        JOIN	stock_picking AS E ON D.picking_id=E.id
                        WHERE   (B.state = 'done')
                    )
                    """
        cr.execute(strSQL)
        
pralon_query_purchasing_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
