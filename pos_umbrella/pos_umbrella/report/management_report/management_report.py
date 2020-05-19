# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []

	columns.append({"fieldname": "si_invoice", "label": "SI Invoice", "fieldtype": "Data", "width": 170})
	columns.append({"fieldname": "posting_date", "label": "Posting Date", "fieldtype": "Data", "width": 170})
	columns.append({"fieldname": "loyalty", "label": "Loyalty", "fieldtype": "Data", "width": 100})
	columns.append({"fieldname": "item_code", "label": "Item Code", "fieldtype": "Data", "width": 150})
	columns.append({"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 200})
	columns.append({"fieldname": "qty", "label": "Qty", "fieldtype": "Data", "width": 80})
	columns.append({"fieldname": "valuation_rate", "label": "Valuation Rate", "fieldtype": "Data", "width": 130})
	columns.append({"fieldname": "selling_amount", "label": "Selling Amount", "fieldtype": "Float", "precision": "2", "width": 130})
	columns.append({"fieldname": "buying_amount", "label": "Buying Amount", "fieldtype": "Float", "precision": "2", "width": 130})
	columns.append({"fieldname": "discount_amount", "label": "Discount", "fieldtype": "Float", "precision": "2", "width": 130})

	columns.append({"fieldname": "net_profit", "label": "Net Profit", "fieldtype": "Float", "precision": "2", "width": 130})
	columns.append({"fieldname": "vat", "label": "VAT", "fieldtype": "Data", "width": 100})
	columns.append({"fieldname": "gross_profit", "label": "Gross Profit", "fieldtype": "Float", "precision": "2", "width": 130})
	columns.append({"fieldname": "gross_profit_percentage", "label": "Gross Profit %", "fieldtype": "Data", "width": 130})

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	pos_profile = filters.get("pos_profile")

	sales_invoices = frappe.db.sql(""" SELECT * FROM `tabSales Invoice` WHERE posting_date BETWEEN %s and %s and pos_profile=%s""",(from_date,to_date,pos_profile), as_dict=1)

	for i in sales_invoices:
		obj = {
			"si_invoice": i.name,
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
