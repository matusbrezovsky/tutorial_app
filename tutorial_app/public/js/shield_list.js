/**
 * Created by matus on 17.4.2018.
 */

$.extend(frappe.listview_settings['Sales Invoice'], {
	onload: function(listview) {
		listview.page.add_menu_item(__("Export to OMEGA"), function() {

			var selected = listview.get_checked_items() || [];

			if(!selected.length) {
				msgprint(__("Neboli vybrané žiadne položky na export."));
				return;
			}

			frappe.call({
				method: "tutorial_app.print_invoices",
				args: {
					list: selected
				},
				callback: function(response) {
					frappe.set_route("Form", 'File', response['message']);


				}
			});

		});
	}
});