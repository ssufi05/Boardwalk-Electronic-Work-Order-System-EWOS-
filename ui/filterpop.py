import tkinter as tk
from tkinter import *
from tkinter import ttk
from database.database_connector import WorkOrdersDB
from tkinter import messagebox
from auth.authentication import Authenticate
from tkinter import simpledialog


class Filter_Window:
    

    def __init__(self, refresh_table_func):
        self.refresh_table_func = refresh_table_func
        self.item_val = None
        self.tree_new_values = None

    def filterPop(self, treeview):  

        db = WorkOrdersDB()
        deptNames = WorkOrdersDB().load_departments()

        def load_data():
            treeview.delete(*treeview.get_children())
            db_rows = db.load_data()
            db.insert_age_format(treeview, db_rows)

        def apply_filter():#on button click check status of all checkbuttons

            filter_list =[]
            filter_dept_list = []
            #Requestor
            filter_list.append(req_name_entry.get().lower())

            #urgency
            if urgent_checkbox.instate(['selected']):
                #print("Urgent")
                filter_list.append('Urgent')
            else:
                filter_list.append('')
            if nonurgent_checkbox.instate(['selected']):
                #print("Nonurgent")
                filter_list.append('')
            else:
                filter_list.append('_')

            #verify at least one urgency type is selected
            if not (urgent_checkbox.instate(['selected']) or nonurgent_checkbox.instate(['selected'])):
                messagebox.showwarning("Warning", "Must select at least one Urgency type")
                return

            #Status
            if submitted_checkbox.instate(['selected']):
                #print("Active")
                filter_list.append('Submitted')
            else:
                filter_list.append('')
            if initiated_checkbox.instate(['selected']):
                #print("Pending")
                filter_list.append('Initiated')
            else:
                filter_list.append('')
            if complete_checkbox.instate(['selected']):
                #print("Complete")
                filter_list.append('Complete')
            else:
                filter_list.append('')

            #verify at least one status is selected
            if not (submitted_checkbox.instate(['selected']) or initiated_checkbox.instate(['selected']) or complete_checkbox.instate(['selected'])):
                messagebox.showwarning("Warning", "Must select at least one Status type")
                return

            filter_list.append(ser_entry.get().lower())

            #departments
            deptBool = False
            for button in dept_button_list:
                if(button.instate(['selected'])):
                    #print(dept_button_list.index(button))
                    filter_dept_list.append(deptNames[dept_button_list.index(button)])
                    deptBool = True #at least one department is selected
                #else:
                    #filter_list.append('')

            if not deptBool:#verify at least one department is selected
                messagebox.showwarning("Warning", "Must select at least one Department")
                return
            else:
                filter_dept_list = str(filter_dept_list).strip("[(,)]")

            #print(filter_list)

            load_data()#refresh the db

            #delete items from treeview
            for item in treeview.get_children():
                #store the values from treeview into a list
                ticket = treeview.item(item)["values"]

                #requestor
                if filter_list[0] != '':#requestor is not empty
                    if not (filter_list[0] in ticket[1].lower()):
                        #print("ticket deleted")
                        treeview.delete(item)
                        continue

                #urgency
                if not ((ticket[4] == filter_list[1]) or (ticket[4] == filter_list[2])):
                        #print("ticket deleted")
                        treeview.delete(item)
                        continue

                #Statuses
                if not ((ticket[3] == filter_list[3]) or (ticket[3] == filter_list[4]) or (ticket[3] == filter_list[5])):
                        #print("ticket deleted")
                        treeview.delete(item)
                        continue

                #Search
                if filter_list[6] != '':#search is not empty
                    if not (filter_list[6] in ticket[6].lower()):
                        #print("ticket deleted")
                        treeview.delete(item)
                        continue
                #departments
                #print(filter_dept_list)
                if ticket[2] not in filter_dept_list:
                    #print("ticket not in dept list")
                    treeview.delete(item)
                    continue

            #close window
            filter_window.destroy()

        
        # Create filter window
        filter_window = Toplevel()
        filter_window.title("Filter")
        filter_window.resizable(False,False)

        filter_frame = ttk.Frame(filter_window)
        filter_frame.pack()

        filter_frame.grab_set()
        filter_frame.focus()

        # Requestor Filter
        req_label = ttk.Label(filter_frame, text = "Requestor:", anchor="w")
        req_label.grid(row=0, column=0, padx=(5,50), pady=(10,0), sticky="ew")
        req_name_entry = ttk.Entry(filter_frame)
        req_name_entry.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="ew")

         # Search Filter
        ser_label = ttk.Label(filter_frame, text = "Search:", anchor="w")
        ser_label.grid(row=2, column=0, padx=(5,50), pady=(10, 0), sticky="ew")
        ser_entry = ttk.Entry(filter_frame)
        ser_entry.grid(row=3, column=0, padx=5, pady=(0, 5), sticky="ew")

        #Urgency Status Filter
        urgent_checkbox = ttk.Checkbutton(filter_frame,text="Urgent")
        urgent_checkbox.grid(row=4, column=0, padx=5, pady=(10,0), sticky="w")
        nonurgent_checkbox = ttk.Checkbutton(filter_frame,text="Nonurgent")
        nonurgent_checkbox.grid(row=5, column=0, padx=5, pady=(10,0), sticky="w")

        urgent_checkbox.state(['!alternate','selected'])
        nonurgent_checkbox.state(['!alternate','selected'])

        #Status Filter
        status_label = ttk.Label(filter_frame, text = "Status:", anchor="w")
        status_label.grid(row=6, column = 0, padx=5, pady=(10,0), sticky="ew")
        #checkbuttons for each status

        submitted_checkbox = ttk.Checkbutton(filter_frame,text="Submitted")
        submitted_checkbox.grid(row=7, column=0, padx=5, pady=(10,0), sticky="w")
        initiated_checkbox = ttk.Checkbutton(filter_frame,text="Initiated")
        initiated_checkbox.grid(row=8, column=0, padx=5, pady=(10,0), sticky="w")
        complete_checkbox = ttk.Checkbutton(filter_frame,text="Complete")
        complete_checkbox.grid(row=9, column=0, padx=5, pady=(10,0), sticky="w")

        submitted_checkbox.state(['!alternate','selected'])
        initiated_checkbox.state(['!alternate','selected'])
        complete_checkbox.state(['!alternate','selected'])

        #Department Filter
        dept_label = ttk.Label(filter_frame, text = "Department:", anchor="e")
        dept_label.grid(row=0, column = 1, padx=(50,10), pady=(10,0), sticky="e")
        dept_button_list = []
        #loop through list of departments and create a checkbutton for each department
        for department in deptNames:
            c = ttk.Checkbutton(filter_frame,text=department)
            c.grid(row=deptNames.index(department)+1, column=1, padx=(20,10), pady=(10,0), sticky="ew")
            c.state(['!alternate','selected'])
            dept_button_list.append(c)

        #determine row for filter button
        row = 10
        if len(deptNames) >= row:
            row = len(deptNames)+1
        #Apply Filter Button
        submit_button = ttk.Button(filter_frame, text="Apply", command=apply_filter) 
        submit_button.grid(row=row, column=0, columnspan=2, padx=5, pady=(15,5), sticky="nsew")
        