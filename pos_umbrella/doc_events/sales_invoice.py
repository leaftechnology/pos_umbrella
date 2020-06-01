import frappe


@frappe.whitelist()
def before_insert_si(doc, method):
    print("JASHDKAHSDKHASJKDH")

    if doc.is_pos:
        doc.outstanding_amount = 0

    try:
        if "loyalty_values" in doc.__dict__:
            print(doc.__dict__['loyalty_values']['number'])
            if doc.__dict__['loyalty_values']['number']:
                loyalty_program = frappe.db.sql(""" SELECT * FROM `tabPOS Profile` WHERE name=%s """,doc.pos_profile, as_dict=1)
                customer = frappe.db.sql(""" SELECT * FROM `tabCustomer` WHERE mobile_no=%s """,doc.__dict__['loyalty_values']['number'], as_dict=1)

                if len(loyalty_program) > 0 and loyalty_program[0].default_loyalty_program:
                    frappe.db.sql(""" UPDATE tabCustomer SET loyalty_program=%s WHERE name=%s """, (loyalty_program[0].default_loyalty_program, customer[0].name))
                    frappe.db.commit()
                    doc.customer = customer[0].name

                if doc.__dict__['loyalty_values']['use_points']:
                    doc.redeem_loyalty_points = 1
                    doc.loyalty_points = doc.__dict__['loyalty_values']['points']

            else:
                loyalty_program = frappe.db.sql(""" SELECT * FROM `tabPOS Profile` WHERE name=%s """, doc.pos_profile,as_dict=1)
                customer = frappe.db.sql(""" SELECT * FROM `tabCustomer` WHERE mobile_no=%s """,doc.pos_profile, as_dict=1)

                if len(loyalty_program) > 0:
                    frappe.db.sql(""" UPDATE tabCustomer SET loyalty_program=%s WHERE name=%s """, ("", customer[0].customer))
                    frappe.db.commit()
                    doc.customer = customer[0].name
    except:
        frappe.log_error(frappe.get_traceback(), "Sales Invoice Creation Failed")

