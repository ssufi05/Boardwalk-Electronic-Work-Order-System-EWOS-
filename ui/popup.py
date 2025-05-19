import tkinter as tk
from tkinter import *
from tkinter import ttk
from database.database_connector import WorkOrdersDB
from tkinter import messagebox
from tkinter import simpledialog
from datetime import datetime
import webbrowser, os



class Pop_Window:

    def __init__(self, refresh_table_func):
        self.refresh_table_func = refresh_table_func
        self.item_val = None
        self.tree_new_values = None

    def modify_db(self, new_values, popupwindow):    
            db = WorkOrdersDB()
            db.update_item(new_values)
            self.refresh_table_func()
            popupwindow.destroy()

    def print(self, values, entries):
        
        if values[1] != entries[0] or values[2] != entries[1] or values[4] != entries[2] or values[5] != entries[3] or values[7] != entries[4] or values[8] != entries[5]:
            confirm = messagebox.askyesno("Confirm", "The printer friendly format will not display \nun-submitted modifications. Continue?")
            if confirm == False or confirm == None:
                return

        html = '''<html>
  <head>
    <style>
      body {{
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        background-color: #f5f5f5;
      }}
      #container {{
        width: 800px;
        margin: 0 auto;
        padding: 2em 0;
      }}
      table {{
        width: 800px;
        border-collapse: collapse;
      }}
      th,
      td {{
        text-align: left;
        padding: 0.5em;
        border-bottom: 1px solid #ddd;
        word-wrap: break-word;
        overflow-wrap: break-word;
        border: 2px solid black;
      }}
      th {{
        background-color: #4CAF50;
        color: white;
        Width: 80px;
      }}
      td {{
        max-width: 300px;
      }}
      tr:nth-child(even) {{
        background-color: #f5f5f5;
      }}
    </style>
  </head>
  <body>
    <div id="container">
      <h1>The Boardwalk EWOS Ticket #{0}</h1>
      <table>
        <thead>
          <tr>
            <th>Requestor</th>
            <td>{1}</td>
          </tr>
          <tr>
            <th>Department</th>
            <td>{2}</td>
          </tr>
          <tr>
            <th>Ticket Status</th>
            <td>{4}</td>
          </tr>
          <tr>
            <th>Urgent Status</th>
            <td>{5}</td>
          </tr>
          <tr>
            <th>Date Requested</th>
            <td>{6}</td>
          </tr>
          <tr>
            <th>Description</th>
            <td>{7}</td>
          </tr>
          <tr>
            <th>Tech Notes</th>
            <td>{8}</td>
          </tr>
          <tr>
            <th>Tech Signature</th>
            <td>{3}</td>
          </tr>
          <tr>
            <th>Date Completed</th>
            <td>{9}</td>
          </tr>
        </thead>
      </table>
    </div>
  </body>
</html>
'''.format(*values)
        
        # Save the HTML to a file
        with open("Print.html", "w") as f:
            f.write(html)

        file_path = os.path.realpath("Print.html")
        webbrowser.open("file://" + file_path)

    def popup(self, item_val):  
        db = WorkOrdersDB()

        deptNames = WorkOrdersDB().load_departments()
        urg=tk.BooleanVar()
        id = item_val[0]
        row = db.get_row_by_id(id)
        dbRowItems = [str(col) for col in row[0]]

        def get_values():
            # Get new values from the user interface
            name = popup_name_entry.get()
            department = PostModDept.get()
            ticket_status = PostModStatus.get()
            urgent_status = "Urgent" if popup_urgent_checkbox.instate(["selected"]) else " "
            notes = popup_notes_entry.get("1.0", "end-1c")
            tech_notes = popup_tech_entry.get("1.0", "end-1c")
            return (name, department, ticket_status, urgent_status, notes, tech_notes, id)

        def modify_row():    #function to mod existing data
            
            new_values = get_values()

            if not db.isntBlank(new_values[0]) or not db.isntBlank(new_values[4]):
                 messagebox.showerror("Error", "Please leave valid input in each field!")
                 return

            if new_values[2] != item_values[4] or new_values[5] != item_values[8]:
                sig = simpledialog.askstring("Confirm", "Technician's digital signature is required to \nmodify technician's notes or status:")
                if not db.isntBlank(sig):
                    messagebox.showwarning("Record not modified", "A signature is required to modify those fields.")
                    popupwindow.grab_set()
                    popupwindow.focus()
                    return
                else:
                    if new_values[2] == "Complete":
                         compdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                         db.insert_completion_date(compdate, id)
                    db.sign(sig, id)

            # Create a new tuple with the updated values
            self.modify_db(new_values, popupwindow)


        item_values = row[0]
        
        urg.set(len(str(item_val[4]))>1)

        # Create popup window
        popupwindow = Toplevel()
        popupwindow.title("Modify Ticket")
        popupwindow.resizable(False,False)
        popupwindow.grab_set()
        popupwindow.focus()

        popup_frame = ttk.Frame(popupwindow)
        popup_frame.pack()

        # Date Requested Label
        date_req_label = ttk.Label(popup_frame, text = "Date Requested: "+str(item_values[6]), anchor="w")
        date_req_label.grid(row=0, column=0, padx=5, pady=(10,0), sticky="ew")


        # ModWindow Name Label
        pop_name_label = ttk.Label(popup_frame, text = "Requestor:", anchor="w")
        pop_name_label.grid(row=1, column=0, padx=5, pady=(10,0), sticky="ew")
        # ModWindow Name Entry Field
        popup_name_entry = ttk.Entry(popup_frame)
        popup_name_entry.insert(0, item_values[1])  # Set default value from selected item
        popup_name_entry.grid(row=2, column=0, padx=5, pady=(0, 5), sticky="ew")

        # ModWindow Department Label
        pop_dept_label = ttk.Label(popup_frame, text = "Department:", anchor="w")
        pop_dept_label.grid(row=3, column=0, padx=5, pady=(10,0), sticky="ew")
        # ModWindow Department Option Menu
        PostModDept=StringVar()
        popup_dept_entry = ttk.OptionMenu(popup_frame, PostModDept, item_values[2], *deptNames)   
        popup_dept_entry.grid(row=4, column=0, padx=5, pady=(0, 5), sticky="ew")

        # ModWindow Urgent Checkbox
        popup_urgent_checkbox = ttk.Checkbutton(popup_frame, text="Urgent", variable = urg)    
        popup_urgent_checkbox.grid(row=7, column=0, padx=5, pady=5, sticky="nsew") 

        # ModWindow Description Label
        pop_desc_label = ttk.Label(popup_frame, text = "Issue Description:", anchor="w")
        pop_desc_label.grid(row=8, column=0, padx=5, pady=(10,0), sticky="ew")
        # ModWindow Description Field
        popup_notes_entry = tk.Text(popup_frame, height=6, width=40, wrap="word")
        popup_notes_entry.insert("1.0", item_values[7])  # Set default value from selected item
        popup_notes_entry.grid(row=9, column=0, padx=5, pady=(0,10), sticky="ew")
        
        # ModWindow Tech Label
        pop_tech_label = ttk.Label(popup_frame, text = "Technician's Notes:", anchor="w")
        pop_tech_label.grid(row=10, column=0, padx=5, pady=(10,0), sticky="ew")
        # ModWindow Tech Field
        popup_tech_entry = tk.Text(popup_frame, height=6, width=40, wrap="word")
        popup_tech_entry.insert("1.0", item_values[8])  
        popup_tech_entry.grid(row=11, column=0, padx=5, pady=(0,10), sticky="ew")
        
        # ModWindow Status Label
        pop_status_label = ttk.Label(popup_frame, text = "Status:", anchor="w")
        pop_status_label.grid(row=12, column=0, padx=5, pady=(10,0), sticky="ew")
        # ModWindow Status Option Menu
        PostModStatus=StringVar()
        popup_status_mod = ttk.OptionMenu(popup_frame, PostModStatus, item_values[4], "Submitted", "Initiated", "Complete")   
        popup_status_mod.grid(row=13, column=0, padx=5, pady=(0,5), sticky="ew")

        # ModWindow Signature Label
        pop_sig_label = ttk.Label(popup_frame, text = ("Tech Signature: " + str(item_values[3])), anchor="w")
        pop_sig_label.grid(row=14, column=0, padx=5, pady=(10,0), sticky="ew")

        # ModWindow Completion Date Label
        date_comp_label = ttk.Label(popup_frame, text = ("Date Completed: " + str(item_values[9])), anchor="w")
        date_comp_label.grid(row=15, column=0, padx=5, pady=(10,10), sticky="ew")

        # ModWindow Submit Button
        popup_submit_button = ttk.Button(popup_frame, text="Submit Revision", command=modify_row) 
        popup_submit_button.grid(row=16, column=0, padx=10, pady=5, sticky="nse")

        #print button
        popup_write_button = ttk.Button(popup_frame, text="Printer Friendly", command=lambda: self.print(dbRowItems, get_values()))
        popup_write_button.grid(row=16, column=0, padx=10, pady=5, sticky="nsw")


        popup_urgent_checkbox.state(['!alternate'])

        popupwindow.mainloop()