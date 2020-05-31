frappe.provide("erpnext.pos");

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
 function loyalty_program(me, number = "", use_points= false, points=0){
	frappe.prompt([
	{'fieldname': 'number', 'fieldtype': 'Data', 'label': 'Mobile Number', 'default': number},
	{'fieldname': 'use_points', 'fieldtype': 'Check', 'label': 'Use Points', 'default': use_points},
	{'fieldname': 'points', 'fieldtype': 'Data', 'label': 'Points', "depends_on": "eval: doc.use_points == 1",  'default': points}
		],
	function(values){
		if (values.number) {
			validate_mobile_number(values, me);
		} else {

			me.update_paid_amount_status(true);
			me.create_invoice();
			me.make_payment();
		}
	},
	'Please Enter Mobile Number For Loyalty',
	'Add or Proceed'
	);
 }
 function validate_mobile_number(values, me){
 	if(values.number[0] === "0"){
		frappe.model.get_value('POS Settings', {'name': 'POS Settings'}, 'allowed_mobile_number_length',
		function(d) {
		  if(values.number.length >= d.allowed_mobile_number_length){
			me.frm.doc.loyalty_values = values;
			me.update_paid_amount_status(true);
			me.create_invoice();
			me.make_payment();
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
 	if(this.frm.doc.outstanding_amount === 0){
		var me = this;
		this.change_status();
		this.update_serial_no()
		if (this.frm.doc.docstatus) {
		    frappe.call({
                method: "pos_umbrella.get_data.update_mobile_number",
                args: {
                    "number": me.frm.doc.loyalty_values.number,
                    "use_points": me.frm.doc.loyalty_values.use_points,
                    "points": me.frm.doc.loyalty_values.points ? me.frm.doc.loyalty_values.points : 0,
                    "loyalty_program": me.pos_profile_data.name,
                    "grand_total": me.frm.doc.grand_total

                },
                async: false,
                callback: function (r) {}
            })
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
}

