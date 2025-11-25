frappe.ui.form.on('Machine Maintenance', {
    refresh: function(frm) {
        show_notes(frm);
        complete_button(frm);
        calculate_total_cost(frm);  
    },

    parts_used_add(frm, cdt, cdn) {
        calculate_total_cost(frm);
    },

    parts_used_remove(frm) {
        calculate_total_cost(frm);
    }
});

frappe.ui.form.on("Parts Used", {
    quantity(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    },

    rate(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    }
});

function calculate_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    let qty = flt(row.quantity);
    let rate = flt(row.rate);

    row.amount = qty * rate;

    frm.refresh_field("parts_used");
    calculate_total_cost(frm);   
}

function calculate_total_cost(frm) {
    let total = 0;

    (frm.doc.parts_used || []).forEach(row => {
        total += flt(row.amount);
    });

    frm.set_value("cost", total);
}

function show_notes(frm) {
    if (frm.fields_dict.notes_html) {
        const crm_notes = new erpnext.utils.CRMNotes({
            frm: frm,
            notes_wrapper: $(frm.fields_dict.notes_html.wrapper)
        });
        crm_notes.refresh();
    }
}

function complete_button(frm) {
    if (frm.doc.status !== "Completed" && !frm.is_new()) {
        frm.add_custom_button("Mark Completed", function() {
            frappe.call({
                method: "craftinteractive.craft_interactive.doctype.machine_maintenance.machine_maintenance.mark_completed",
                args: { 
                    docname: frm.doc.name 
                },
                callback: function() {
                    frm.reload_doc();
                }
            });
        });
    }
}
