# Copyright (c) 2013, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	pos_profile = filters.get("pos_profile")
	print(filters.get("with_details"))
	with_details = filters.get("with_details")

	if from_date > to_date:
		frappe.throw("From Date should be before To Date")
	else:
		columns.append({"fieldname": "store_name", "label": "Store Name", "fieldtype": "Data", "width": 150})

		if with_details:
			columns.append({"fieldname": "invoice_number", "label": "Invoice Number", "fieldtype": "Link", "options": "Sales Invoice", "width": 150})

			columns.append({"fieldname": "item_code", "label": "Item_code", "fieldtype": "Data", "width": 120})
			columns.append({"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 230})
			columns.append({"fieldname": "quantity", "label": "Quantity", "fieldtype": "Data", "width": 100})
			columns.append({"fieldname": "rate", "label": "Rate", "fieldtype": "Data", "width": 100})
			columns.append({"fieldname": "amount", "label": "Amount", "fieldtype": "Data", "width": 100})



		columns.append({"fieldname": "discount", "label": "Discount", "fieldtype": "Data", "width": 100})
		columns.append({"fieldname": "write_off", "label": "Write Off", "fieldtype": "Data", "width": 100})
		columns.append({"fieldname": "loyalty", "label": "Loyalty", "fieldtype": "Data", "width": 100})
		columns.append({"fieldname": "net_sale", "label": "Net Sale", "fieldtype": "Data", "width": 100})
		columns.append({"fieldname": "vat", "label": "VAT", "fieldtype": "Data", "width": 100})
		columns.append({"fieldname": "gross_sale", "label": "Gross Sale", "fieldtype": "Data", "width": 100})
		condition = ""

		if pos_profile:
			condition += " and pos_profile='{0}' ".format(pos_profile)

		if with_details:
			condition += " and is_pos=1"

		condition += " ORDER By pos_profile ASC"

		query = """ SELECT * FROM `tabSales Invoice` 
				WHERE docstatus=1 and posting_date BETWEEN '{0}' and '{1}' {2}""".format(from_date, to_date,condition)
		print(query)
		sales_invoices = frappe.db.sql(query, as_dict=True)

		for idx,i in enumerate(sales_invoices):
			if not with_details:
				obj = {
					"invoice_number": i.name,
					"store_name": i.pos_profile,
					"discount": i.discount_amount,
					"write_off": i.write_off_amount,
					"loyalty": i.loyalty_amount,
					"net_sale": i.total,
					"gross_sale": i.grand_total,
					"vat": i.total_taxes_and_charges,
				}
				mode_of_payments = frappe.db.sql(""" SELECT * FROM `tabSales Invoice Payment` WHERE parent=%s """,i.name,as_dict=True)
				for ii in mode_of_payments:
					check_mop(columns,ii)
					obj[ii.mode_of_payment] = ii.amount

				data.append(obj)
			else:
				obj = {}
				obj["invoice_number"] = i.name
				obj["store_name"] = i.pos_profile

				invoice_items = frappe.db.sql(""" SELECT * FROM `tabSales Invoice Item` WHERE parent=%s""", i.name, as_dict=1)
				for idxx,x in enumerate(invoice_items):
					if idxx == 0:

						obj["item_code"] = x.item_code
						obj["item_name"] = x.item_name
						obj["quantity"] = x.qty
						obj["rate"] = x.rate
						obj["amount"] = x.amount

						obj["discount"] = i.discount_amount
						obj["write_off"] = i.write_off_amount
						obj["loyalty"] = i.loyalty_amount
						obj["net_sale"] = i.total
						obj["gross_sale"] = i.grand_total
						obj["vat"] = i.total_taxes_and_charges

						mode_of_payments = frappe.db.sql(""" SELECT * FROM `tabSales Invoice Payment` WHERE parent=%s """,
														 i.name, as_dict=True)
						for ii in mode_of_payments:
							check_mop(columns, ii)
							obj[ii.mode_of_payment] = ii.amount

					else:
						obj = {}
						obj["item_code"] = x.item_code
						obj["item_name"] = x.item_name
						obj["quantity"] = x.qty
						obj["rate"] = x.rate
						obj["amount"] = x.amount
					data.append(obj)

	return columns, data

def check_mop(columns, ii):
	add = True
	for i in columns:
		if i.get("label") == ii.mode_of_payment:
			add = False
	if add:
		columns.append({
			"fieldname": ii.mode_of_payment,
			"label": ii.mode_of_payment,
			"fieldtype": "Data",
			"width": 150
		})