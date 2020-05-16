import frappe

@frappe.whitelist()
def get_company_address(address):
    address = frappe.db.sql(""" SELECT * FROM `tabAddress` WHERE name=%s """, address, as_dict=True)
    if len(address) > 0:
        return address[0].address_line1
    return ""

@frappe.whitelist()
def get_phone_number(company):

    company_record = frappe.db.sql(""" SELECT * FROM `tabCompany` WHERE name=%s """, company, as_dict=True)
    if len(company_record) > 0:
        return company_record[0].phone_no,company_record[0].tax_id
    return ""