import frappe


@frappe.whitelist()
def check_outstanding(doc, method):
    # print(doc.outstanding_amount)
    # if doc.outstanding_amount <=0:
    #     frappe.throw("Outstanding must be greater than 0")
    pass