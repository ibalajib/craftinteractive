// Copyright (c) 2025, Balaji B and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Machine Maintenance Report"] = {
	formatter(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (!data || !data.status) {
            return value;
        }

        let color = "";

        if (data.status === "Overdue") {
            color = "background-color:#ffcccc !important;";   // light red
        }
        else if (data.status === "Scheduled") {
            color = "background-color:#fff2b3 !important;";   // light yellow
        }
        else if (data.status === "Completed") {
            color = "background-color:#d6f5d6 !important;";   // light green
        }

        return `<span style="${color} display:block; width:100%; height:100%;">${value}</span>`;
    },
	"filters": [
		{
        "fieldname": "machine_name",
        "label": "Machine",
        "fieldtype": "Link",
        "options": "Item"
    },
    {
        "fieldname": "technician",
        "label": "Technician",
        "fieldtype": "Link",
        "options": "Employee"
    },
    {
        "fieldname": "from_date",
        "label": "From Date",
        "fieldtype": "DateRange"
    },
    {
        "fieldname": "consolidated",
        "label": "Consolidated",
        "fieldtype": "Check",
        "default": 0
    }
	]
};
