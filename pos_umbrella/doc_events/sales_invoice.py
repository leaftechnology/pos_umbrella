import frappe


@frappe.whitelist()
def before_insert_si(doc, method):
    print("DOOOOOCCCCCCC")
    try:
        if "loyalty_values" in doc.__dict__:
            if doc.__dict__['loyalty_values']['number']:
                loyalty_program = frappe.db.sql(""" SELECT * FROM `tabPOS Profile` WHERE name=%s """,doc.pos_profile, as_dict=1)
                if len(loyalty_program) > 0 and loyalty_program[0].default_loyalty_program:
                    frappe.db.sql(""" UPDATE tabCustomer SET loyalty_program=%s WHERE name=%s """, (loyalty_program[0].default_loyalty_program, loyalty_program[0].customer))
                    frappe.db.commit()

                if doc.__dict__['loyalty_values']['use_points']:
                    doc.redeem_loyalty_points = 1
                    doc.loyalty_points = doc.__dict__['loyalty_values']['points']

            else:
                loyalty_program = frappe.db.sql(""" SELECT * FROM `tabPOS Profile` WHERE name=%s """, doc.pos_profile,
                                                as_dict=1)
                if len(loyalty_program) > 0:
                    frappe.db.sql(""" UPDATE tabCustomer SET loyalty_program=%s WHERE name=%s """,
                                  ("", loyalty_program[0].customer))
                    frappe.db.commit()
    except:
        frappe.log_error(frappe.get_traceback(), "Sales Invoice Creation Failed")