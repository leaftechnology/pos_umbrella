# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []

	columns.append({"fieldname": "si_invoice", "label": "SI Invoice", "fieldtype": "Link", "width": 170, "options": "Sales Invoice"})
	columns.append({"fieldname": "store_name", "label": "Store Name", "fieldtype": "Link", "width": 170, "options": "Sales Invoice"})
	columns.append({"fieldname": "posting_date", "label": "Posting Date", "fieldtype": "Data", "width": 170})
	columns.append({"fieldname": "loyalty", "label": "Loyalty", "fieldtype": "Data", "width": 100})
	columns.append({"fieldname": "item_code", "label": "Item Code", "fieldtype": "Data", "width": 150})
	columns.append({"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 200})
	columns.append({"fieldname": "qty", "label": "Qty", "fieldtype": "Data", "width": 80})
	columns.append({"fieldname": "valuation_rate", "label": "Valuation Rate", "fieldtype": "Data", "width": 130})
	columns.append({"fieldname": "selling_amount", "label": "Selling Amount", "fieldtype": "Float", "precision": "3", "width": 130})
	columns.append({"fieldname": "buying_amount", "label": "Buying Amount", "fieldtype": "Float", "precision": "3", "width": 130})
	columns.append({"fieldname": "discount_amount", "label": "Discount", "fieldtype": "Float", "precision": "3", "width": 130})

	columns.append({"fieldname": "net_profit", "label": "Net Profit", "fieldtype": "Float", "precision": "3", "width": 130})
	columns.append({"fieldname": "vat", "label": "VAT", "fieldtype": "Float", "width": 100, "precision": "3"})
	columns.append({"fieldname": "gross_profit", "label": "Gross Profit", "fieldtype": "Float", "precision": "3", "width": 130})
	columns.append({"fieldname": "gross_profit_percentage", "label": "Gross Profit %", "fieldtype": "Data", "width": 130})

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	pos_profile = filters.get("pos_profile")
	warehouse = filters.get("warehouse")

	condition = ""

	if warehouse:
		for idx, warehouse1 in enumerate(warehouse):
			if idx == 0:
				condition += " and "
			else:
				condition += " or "
			condition += " set_warehouse='{0}' ".format(warehouse1)


	if pos_profile:
		for idx, pos in enumerate(pos_profile):
			if idx == 0:
				condition += " and "
			else:
				condition += " or "
			condition += " pos_profile='{0}' ".format(pos)

	if condition:
		condition += " ORDER BY pos_profile ASC"

	query = """ SELECT * FROM `tabSales Invoice` WHERE posting_date BETWEEN '{0}' and '{1}' {2}""".format(from_date,to_date,condition)
	sales_invoices = frappe.db.sql(query, as_dict=1)

	for i in sales_invoices:
		obj = {
			"si_invoice": i.name,
			"store_name": i.pos_profile,
			"posting_date": i.posting_date,
			"loyalty": i.loyalty_amount,
		}

		sales_invoice_items = frappe.db.sql(""" SELECT * FROM `tabSales Invoice Item` WHERE parent=%s """, i.name, as_dict=1)
		for idx,ii in enumerate(sales_invoice_items):
			selling = frappe.db.sql(""" SELECT * FROM `tabItem Price` WHERE item_code=%s and selling=1 ORDER BY valid_from DESC """, ii.item_code, as_dict=1)
			valuation_rate = frappe.db.sql(""" SELECT * FROM `tabItem` WHERE name=%s """, ii.item_code, as_dict=1)

			if idx != 0:
				obj = {}
			buying_amount =  valuation_rate[0].valuation_rate if len(valuation_rate) > 0 else ii.rate
			obj['item_code'] = ii.item_code
			obj['item_name'] = ii.item_name
			obj['qty'] = ii.qty
			obj['valuation_rate'] = valuation_rate[0].valuation_rate
			obj['buying_amount'] = buying_amount
			obj['selling_amount'] = ii.rate
			obj['discount_amount'] = ii.discount_amount
			obj['vat'] = i.total_taxes_and_charges
			obj['net_profit'] = (ii.rate - buying_amount) * ii.qty
			obj['gross_profit'] = (ii.rate - buying_amount) * ii.qty
			if ii.rate > 0:
				print("NAA MAN")
				print(round((((ii.rate - buying_amount) * ii.qty) / ii.rate ) * 100))
				obj['gross_profit_percentage'] = str(round((((ii.rate - buying_amount) * ii.qty) / ii.rate ) * 100,2)) + "%"
			else:
				obj['gross_profit_percentage'] = "0%"

			data.append(obj)


	return columns, data
