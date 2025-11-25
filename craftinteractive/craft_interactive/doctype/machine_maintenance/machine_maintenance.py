# Copyright (c) 2025, Balaji B and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.crm.utils import CRMNote
from erpnext.accounts.doctype.journal_entry.journal_entry import get_exchange_rate
from frappe.utils import today, getdate,flt



class MachineMaintenance(CRMNote, Document):

    def before_save(self):
        self.status_update()
    
    def validate(self):
        self.status_update()
        if self.workflow_state == "Completed":
            if not self.completion_date:
                frappe.throw("Please set a Completion Date before marking the maintenance as Completed.")


    def status_update(self):
        maintenance_date = getdate(self.maintenance_date)
        current_date = getdate(today())

        if maintenance_date < current_date and self.status != "Completed":
            self.status = "Overdue"
    
    def before_submit(self):
        self.validate_technician()
        total_cost = self.get_total_cost()
        self.create_journal_entry(total_cost)

    def validate_technician(self):
        if not self.technician:
            frappe.throw("Technician must be assigned before submitting.")

    def get_total_cost(self):
        total = 0
        for d in self.parts_used:
            total += flt(d.amount)
        return total

    def create_journal_entry(self, amount):
        if amount <= 0:
            frappe.msgprint("No parts used. Skipping Journal Entry.")
            return
        company_abbr = frappe.db.get_value("Company", self.company, "abbr")

        EXPENSE_ACCOUNT = f"Office Maintenance Expenses - {company_abbr}"
        PAYMENT_ACCOUNT = f"Cash - {company_abbr}"
        
        je = frappe.new_doc("Journal Entry")
        je.voucher_type = "Journal Entry"
        je.posting_date = today()
        je.user_remark = f"Auto-generated from Machine Maintenance {self.name}"


        je.append("accounts", {
            "account": EXPENSE_ACCOUNT,
            "debit_in_account_currency": amount,
            "credit_in_account_currency": 0
        })

        je.append("accounts", {
            "account": PAYMENT_ACCOUNT,
            "credit_in_account_currency": amount,
            "debit_in_account_currency": 0
        })

        je.insert()
        je.submit()
        frappe.msgprint(f"Journal Entry againist {self.name} is created.")

@frappe.whitelist()
def mark_completed(docname):
    doc = frappe.get_doc("Machine Maintenance", docname)
    if doc.status != "Overdue":
        doc.status = "Completed"
    doc.completion_date = today()
    doc.save()
    frappe.msgprint("Maintenance marked as Completed.")
