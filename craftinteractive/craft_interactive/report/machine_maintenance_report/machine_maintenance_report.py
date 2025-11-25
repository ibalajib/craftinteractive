import frappe

def execute(filters=None):
    filters = filters or {}
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    if filters.get("consolidated"):
        return [
            {"label": "Machine", "fieldname": "machine_name", "fieldtype": "Link", "options": "Item", "width": 200},
            {"label": "Total Cost", "fieldname": "cost", "fieldtype": "Currency", "width": 150},
        ]

    return [
        {"label": "Machine", "fieldname": "machine_name", "fieldtype": "Link", "options": "Item", "width": 200},
        {"label": "Maintenance Date", "fieldname": "maintenance_date", "fieldtype": "Date", "width": 200},
        {"label": "Technician", "fieldname": "technician", "fieldtype": "Link", "options": "Employee", "width": 200},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 200},
        {"label": "Cost", "fieldname": "cost", "fieldtype": "Currency", "width": 200},
        {"label": "Row Color", "fieldname": "color", "fieldtype": "Data", "hidden": 1},
    ]


def get_data(filters):

    conditions = "" 

    if filters.get("machine_name"):
        conditions += " AND machine_name = %(machine_name)s"

    # Technician filter
    if filters.get("technician"):
        conditions += " AND technician = %(technician)s"

    # DateRange filter
    if filters.get("from_date"):
        start_date, end_date = filters.get("from_date")
        
        filters["start_date"] = start_date
        filters["end_date"] = end_date

        conditions += " AND maintenance_date BETWEEN %(start_date)s AND %(end_date)s"


    records = frappe.db.sql("""
    SELECT 
        name, machine_name, maintenance_date, technician, status, cost
    FROM `tabMachine Maintenance`
    WHERE docstatus < 2 {conditions}
    ORDER BY maintenance_date DESC
""".format(conditions=conditions), filters, as_dict=True)

    if filters.get("consolidated"):
        return consolidate(records)

    return highlight(records)


def consolidate(records):
    summary = {}

    for d in records:
        summary.setdefault(d.machine_name, 0)
        summary[d.machine_name] += d.cost or 0

    result = []
    for machine, total in summary.items():
        result.append({
            "machine_name": machine,
            "cost": total
        })

    return result



def highlight(records):
    for d in records:
        if d.status == "Overdue":
            d["color"] = "red"
        elif d.status == "Scheduled":
            d["color"] = "yellow"
        elif d.status == "Completed":
            d["color"] = "green"
        else:
            d["color"] = ""
    return records
