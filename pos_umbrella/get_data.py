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


@frappe.whitelist()
def update_mobile_number(number,use_points,points,loyalty_program, grand_total):
    if not use_points:
        if not frappe.db.exists("Mobile Numbers", number):
            frappe.get_doc({
                "doctype": "Mobile Numbers",
                "mobile_number": number
            }).insert(ignore_permissions=1)

        loyalty_program_collection = frappe.db.sql(""" SELECT * FROM `tabLoyalty Program Collection` WHERE parent=%s """,(loyalty_program),as_dict=1)

        if len(loyalty_program_collection) > 0:
            points = int(float(grand_total) / float(loyalty_program_collection[0].collection_factor))

            frappe.db.sql(""" UPDATE `tabMobile Numbers` SET balance=%s WHERE name=%s""", (points, number))
            frappe.db.commit()
    else:
        if not frappe.db.exists("Mobile Numbers", number):
            frappe.get_doc({
                "doctype": "Mobile Numbers",
                "mobile_number": number
            }).insert(ignore_permissions=1)
        mobile_number = frappe.db.sql(""" SELECT * FROM `tabMobile Numbers` WHERE name=%s """,number, as_dict=1)
        diff = int(mobile_number[0].balance) - int(points)

        frappe.db.sql(""" UPDATE `tabMobile Numbers` SET balance=%s WHERE name=%s""", (diff, number))
        frappe.db.commit()