frappe.provide("erpnext.pos");
var enable_submit_and_print = 0
erpnext.payments.prototype.set_payment_primary_action = function () {
	var me = this
  if(enable_submit_and_print === "1"){
		this.dialog.set_primary_action(__("Submit and Print"), function() {
		// Allow no ZERO payment
		$.each(me.frm.doc.payments, function (index, data) {
			if (data.amount != 0) {
				me.dialog.hide();
				me.submit_invoice();
				return;
			}
		});
	})
  } else {
		this.dialog.set_primary_action(__("Submit"), function() {
			// Allow no ZERO payment
			$.each(me.frm.doc.payments, function (index, data) {
				if (data.amount != 0) {
					me.dialog.hide();
					me.submit_invoice();
					return;
				}
			});
		})
  }

}
erpnext.pos.PointOfSale.prototype.bind_numeric_keypad = function () {
 	var me = this;
		$(this.numeric_keypad).find('.pos-operation').on('click', function(){
			me.numeric_val = '';
		})

		$(this.numeric_keypad).find('.numeric-keypad').on('click', function(){
			me.numeric_id = $(this).attr("id") || me.numeric_id;
			me.val = $(this).attr("val")
			if(me.numeric_id) {
				me.selected_field = $(me.wrapper).find('.selected-item').find('.' + me.numeric_id)
			}

			if(me.val && me.numeric_id) {
				me.numeric_val += me.val;
				me.selected_field.val(flt(me.numeric_val))
				me.selected_field.trigger("change")
				// me.render_selected_item()
			}

			if(me.numeric_id && $(this).hasClass('pos-operation')) {
				me.numeric_keypad.find('button.pos-operation').removeClass('active');
				$(this).addClass('active');

				me.selected_row.find('.pos-list-row').removeClass('active');
				me.selected_field.closest('.pos-list-row').addClass('active');
			}
		})

		$(this.numeric_keypad).find('.numeric-del').click(function(){
			if(me.numeric_id) {
				me.selected_field = $(me.wrapper).find('.selected-item').find('.' + me.numeric_id)
				me.numeric_val = cstr(flt(me.selected_field.val())).slice(0, -1);
				me.selected_field.val(me.numeric_val);
				me.selected_field.trigger("change")
			} else {
				//Remove an item from the cart, if focus is at selected item
				me.remove_selected_item()
			}
		})

		$(this.numeric_keypad).find('.pos-pay').click(function(){
			me.validate();
            console.log(me)
			validate_loyalty_program(me)
		})
 }
 function validate_loyalty_program(me){
	frappe.model.get_value('POS Settings', {'name': 'POS Settings'}, 'loyalty_program',
	  function(d) {
		  if(d.loyalty_program === "1"){
			loyalty_program(me);
		  } else {
			me.update_paid_amount_status(true);
			me.create_invoice();
			me.make_payment();
		  }
	  });
 }
 function loyalty_program(me, number = "", use_points= false, points=0, current_points = 0){

	var prompt = frappe.prompt([
		{'fieldname': 'number', 'fieldtype': 'Data', 'label': 'Mobile Number', 'default': number},
		{'fieldname': 'get_points', 'fieldtype': 'Button', 'label': "Get Points"},
		{'fieldname': 'current_points','fieldtype': 'Int', 'label': 'Current Points', "default": current_points, "read_only": "1"},
		{'fieldname': 'use_points', 'fieldtype': 'Check', 'label': 'Use Points', 'default': use_points, "depends_on": "eval: doc.current_points > 0"},
		{'fieldname': 'points', 'fieldtype': 'Data', 'label': 'Points', "depends_on": "eval: doc.use_points == 1",  'default': points}
	],
	function(values){
		if (values.number) {
			validate_mobile_number(values, me);
		} else {
			me.frm.doc.loyalty_values = {}
			me.update_paid_amount_status(true);
			me.create_invoice();
			me.make_payment();
		}
	},
	'Please Enter Mobile Number For Loyalty',
	'Add or Proceed'
	);
	prompt.fields_dict.get_points.$input.click(function() {
		if(prompt.fields_dict.number.$input.val()){

			frappe.call({
			method: "frappe.client.get",
			args: {
				"doctype": "Mobile Numbers",
				"name": prompt.fields_dict.number.$input.val()

			},
			callback: function (r) {
				if(r.message && r.message.balance > 0){
					prompt.hide();
					var number = prompt.fields_dict.number.$input.val();
					var points = prompt.fields_dict.points.$input.val();
					loyalty_program(me, number, false, points, r.message.balance);
				} else {
					frappe.msgprint("Current balance is 0")

				}

            }
		});
		} else {
			frappe.msgprint("Input valid number")
		}

	})
 }

 function validate_mobile_number(values, me){
 	if(values.number[0] === "0"){
		frappe.model.get_value('POS Settings', {'name': 'POS Settings'}, 'allowed_mobile_number_length',
		function(d) {
		  if(values.number.length >= d.allowed_mobile_number_length){
			me.frm.doc.loyalty_values = values;

			me.update_paid_amount_status(true);
			if(values.use_points && parseInt(values.points) > 0){
				console.log("POINTS")
				console.log(values.points)
				console.log(me.frm.doc.grand_total)
				console.log(me.frm.doc.paid_amount)
				me.frm.doc.base_net_total = me.frm.doc.base_net_total - parseInt(values.points)
				me.frm.doc.base_grand_total = me.frm.doc.base_grand_total - parseInt(values.points)
				me.frm.doc.base_paid_amount = me.frm.doc.base_paid_amount - parseInt(values.points)
				me.frm.doc.base_total = me.frm.doc.base_total - parseInt(values.points)
				me.frm.doc.net_total = me.frm.doc.net_total - parseInt(values.points)
				me.frm.doc.total = me.frm.doc.total - parseInt(values.points)
				me.frm.doc.grand_total = me.frm.doc.grand_total - parseInt(values.points)
				me.frm.doc.paid_amount = me.frm.doc.paid_amount - parseInt(values.points)
				me.frm.doc.payments[0].amount = me.frm.doc.payments[0].amount - parseInt(values.points)
				me.frm.doc.payments[0].base_amount = me.frm.doc.payments[0].base_amount - parseInt(values.points)
				me.frm.doc.outstanding = 0
			}
			me.create_invoice();
			me.make_payment();
			console.log(values.use_points)

		  } else {
			  frappe.msgprint("Minimum Allowed Mobile Number Length is " + d.allowed_mobile_number_length)
			  loyalty_program(me, values.number, values.use_points, values.points)
		  }
		});
	} else {
		frappe.msgprint("Number must start with 0")
		loyalty_program(me,values.number,values.use_points,values.points)
			}

 }

 erpnext.pos.PointOfSale.prototype.submit_invoice = function () {
 	if (this.frm.doc.outstanding_amount === 0){
		var me = this;
		this.change_status();
		this.update_serial_no()
		if (this.frm.doc.docstatus === 1) {
			if(me.frm.doc.loyalty_values && me.frm.doc.loyalty_values.number){
				frappe.call({
					method: "pos_umbrella.get_data.update_mobile_number",
					args: {
						"number": me.frm.doc.loyalty_values.number,
						"use_points": me.frm.doc.loyalty_values.use_points ? me.frm.doc.loyalty_values.use_points : false,
						"points": me.frm.doc.loyalty_values.points ? me.frm.doc.loyalty_values.points : 0,
						"loyalty_program": me.pos_profile_data.name,
						"grand_total": me.frm.doc.grand_total

					},
					async: false,
					callback: function (r) {}
				})
			}
			if(enable_submit_and_print === "1"){
				// this.create_new()

				var html = frappe.render(me.print_template_data, me.frm.doc);
				me.print_document(html);
			  } else {
				this.print_dialog()
			  }

		}
	} else {
		frappe.msgprint("Outstanding amount must be 0")
	}
 }
erpnext.pos.PointOfSale.prototype.make_menu_list = function () {
	var me = this;
	this.page.clear_menu();

	// for mobile
	this.page.add_menu_item(__("Pay"), function () {
		me.validate();
		me.update_paid_amount_status(true);
		me.create_invoice();
		me.make_payment();
	}).addClass('visible-xs');

	this.page.add_menu_item(__("New Sales Invoice"), function () {
		me.save_previous_entry();
		me.create_new();
	})

	this.page.add_menu_item(__("Sync Master Data"), function () {
		me.get_data_from_server(function () {
			me.load_data(false);
			me.make_item_list();
			me.set_missing_values();
		})
	});

	this.page.add_menu_item(__("Sync Offline Invoices"), function () {
		me.freeze_screen = true;
		me.sync_sales_invoice()
	});

	this.page.add_menu_item(__("Cashier Closing"), function () {
		frappe.set_route('List', 'Cashier Closing');
	});

	this.page.add_menu_item(__("POS Profile"), function () {
		frappe.set_route('List', 'POS Profile');
	});
	this.page.add_menu_item(__("Reset"), function () {
		try {
			localStorage.setItem('sales_invoice_doc', JSON.stringify([]));
			frappe.msgprint("Reset Done")
		} catch (e) {
			frappe.throw(__("LocalStorage is full , did not save"))
		}
	});
},

erpnext.pos.PointOfSale.prototype.create_new = function () {
		frappe.model.get_value('POS Settings', {'name': 'POS Settings'}, 'enable_submit_and_print',
		  function(d) {
			  enable_submit_and_print = d.enable_submit_and_print
		  });
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
}

