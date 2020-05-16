frappe.provide("erpnext.pos");

erpnext.pos.PointOfSale.prototype.submit_invoice = function () {
	this.frm.doc.test = "TEEEEST"
	console.log(this.frm.doc.test)
	console.log(this.frm.doc)
 	if(this.frm.doc.outstanding_amount === 0){
		var me = this;
		this.change_status();
		this.update_serial_no()
		if (this.frm.doc.docstatus) {
			this.print_dialog()
			// var html = frappe.render(me.print_template_data, me.frm.doc);
			// me.print_document(html);
		}
	} else {
		frappe.msgprint("Outstanding amount must be 0")
	}
 }
erpnext.pos.PointOfSale.prototype.create_new = function () {
		var me = this;
		this.frm = {}
		this.load_data(true);
		this.frm.doc.offline_pos_name = '';
		this.setup();
		this.set_default_customer()
		frappe.call({
			method: "pos_umbrella.get_data.get_company_address",
			args: {
				"address": me.pos_profile_data.company_address
			},
			async: false,
			callback: function (r) {
				me.frm.doc.company_address_value = r.message
			}
		})
		frappe.call({
			method: "pos_umbrella.get_data.get_phone_number",
			args: {
				"company": me.frm.doc.company
			},
			async: false,
			callback: function (r) {
				me.frm.doc.phone_number = r.message[0]
				me.frm.doc.vat = r.message[1]
			}
		})
	console.log(this.frm.doc)
	console.log(me)
}

