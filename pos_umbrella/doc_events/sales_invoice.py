import frappe


@frappe.whitelist()
def before_insert_si(doc, method):
    print("JASHDKAHSDKHASJKDH")

    if doc.is_pos:
        doc.outstanding_amount = 0

    try:
        if "loyalty_values" in doc.__dict__:
            if "number" in doc.__dict__['loyalty_values'] and doc.__dict__['loyalty_values']['number']:
                loyalty_program = frappe.db.sql(""" SELECT * FROM `tabPOS Profile` WHERE name=%s """,doc.pos_profile, as_dict=1)
                customer = frappe.db.sql(""" SELECT * FROM `tabCustomer` WHERE mobile_no=%s """,doc.__dict__['loyalty_values']['number'], as_dict=1)

                if len(loyalty_program) > 0 and loyalty_program[0].default_loyalty_program:
                    frappe.db.sql(""" UPDATE tabCustomer SET loyalty_program=%s WHERE name=%s """, (loyalty_program[0].default_loyalty_program, customer[0].name))
                    frappe.db.commit()
                    doc.customer = customer[0].name

                if "use_points" in doc.__dict__['loyalty_values'] and doc.__dict__['loyalty_values']['use_points']:
                    loyalty_program_record = frappe.db.sql(""" SELECT * FROM `tabLoyalty Program` WHERE name= %s""", (loyalty_program[0].default_loyalty_program), as_dict=1)
                    doc.redeem_loyalty_points = 1
                    doc.loyalty_points = int(doc.__dict__['loyalty_values']['points'])
                    doc.loyalty_redemption_account = loyalty_program_record[0].expense_account
                    doc.loyalty_redemption_cost_center = loyalty_program_record[0].cost_center

            else:
                loyalty_program = frappe.db.sql(""" SELECT * FROM `tabPOS Profile` WHERE name=%s """, doc.pos_profile,as_dict=1)
                customer = frappe.db.sql(""" SELECT * FROM `tabCustomer` WHERE mobile_no=%s """,doc.pos_profile, as_dict=1)

                if len(loyalty_program) > 0:
                    frappe.db.sql(""" UPDATE tabCustomer SET loyalty_program=%s WHERE name=%s """, ("", customer[0].customer))
                    frappe.db.commit()
                    doc.customer = customer[0].name
    except:
        frappe.log_error(frappe.get_traceback(), "Sales Invoice Creation Failed")

@frappe.whitelist()
def validate_si(doc, method):

    if doc.redeem_loyalty_points and doc.loyalty_points > 0 and doc.loyalty_amount > 0:
        pass

@frappe.whitelist()
def after_submit_si(doc, method):

    if doc.redeem_loyalty_points and doc.loyalty_points > 0 and doc.loyalty_amount > 0:
        grand_total = doc.grand_total - doc.loyalty_amount
        frappe.db.set_value("Sales Invoice", doc.name, "grand_total", grand_total)
        frappe.db.set_value("Sales Invoice", doc.name, "outstanding_amount", 0)


