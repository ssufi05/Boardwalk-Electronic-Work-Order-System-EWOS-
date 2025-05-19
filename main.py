from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from database.database_connector import WorkOrdersDB
from tkinter import simpledialog
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfile
from ui.themes import sv_ttk
from ui import *
from auth.authentication import Authenticate
import configparser
import mysql.connector
from ui.popup import Pop_Window
from ui.filterpop import Filter_Window




db = WorkOrdersDB()
auth = Authenticate()

def load_data():                                # Refresh Treeview with DB contents
    treeview.delete(*treeview.get_children())
    db_rows = db.load_data()
    db.insert_age_format(treeview, db_rows)
    sort_treeview(treeview, ' ID', True)

def insert_row():                               # Generate a new ticket from user input
    name = name_entry.get()
    department = depSelection.get()
    ticket_status = "Submitted"
    urgent_status = "Urgent" if urgent_checkbox.instate(["selected"]) else " "
    date = db.time()
    notes = notes_entry.get("1.0",'end-1c')

    row_values = [name, department, "", ticket_status, urgent_status, date, notes, "", ""]

    if (department !="Select a Department") and db.isntBlank(notes) and db.isntBlank(name): #test for valid input 
        db.insert(row_values)# Insert the data into the MySQL database
        load_data()

        # Clear the values
        name_entry.delete(0, "end")
        name_entry.insert(0, "")
        depSelection.set("Select a Department")
        urgent_checkbox.state(["!selected"])
        notes_entry.delete(1.0, "end-1c")
        notes_entry.insert(1.0, "")
        load_data()

    else:
        messagebox.showerror("Invalid input", "Please populate all fields with valid input.")

def delete_row():                               # Delete one or multiple entries
    victims = treeview.selection()
    x = len(victims)
    if not victims:
        return
    else:
        # password requirement
        password = simpledialog.askstring("Are you sure?", "Enter password to delete " + str(x) + " records:", show="*")
        if password == None:
            return
        
        if auth.authenticate(auth.hash_password(password)) == True:
            for item in victims:
                id = treeview.item(item, 'values')[0]
                db.delete_item(id) # Delete from DB

            load_data()
            messagebox.showinfo("Deletion Success", str(x) + " record(s) deleted.")
        else:
            messagebox.showerror("Incorrect Password", "Incorrect password.")

def toggle_mode():                              # Toggle light/dark mode
    if mode_switch.instate(["selected"]):
        sv_ttk.set_theme("dark")
    else:
        sv_ttk.set_theme("light")
    
def sort_treeview(tree, col, descending):       # Sorting logic for ID/Requested- default for other cols
    data = [(tree.set(item, col), item) for item in tree.get_children('')]
    if col == "Requested":
        sort_treeview(tree, ' ID', descending)
        return
    if col == " ID":
        data.sort(key=lambda x: int(x[0]), reverse=descending)
        tree.heading(" ID", command=lambda: sort_treeview(tree, col, not descending))
        tree.heading("Requested", command=lambda: sort_treeview(tree, col, not descending))
    else:
        data.sort(reverse=descending)
        tree.heading(col, command=lambda: sort_treeview(tree, col, not descending))

    for index, (val, item) in enumerate(data):
        tree.move(item, '', index)

def open_popup():                               # Open the View/Modify interface
    o = Pop_Window(load_data)

    selected_item = treeview.selection()
    x = len(treeview.selection())
    if x==0:
        return
    if x>1:
        messagebox.showwarning("Invalid", "You can only modify one entry at a time!")
        return
    else:
        item_val = treeview.item(selected_item, "values")
        o.popup(item_val)

def filter_popup():                             # Opens the Filter dialog
    o = Filter_Window(load_data)
    o.filterPop(treeview)

def bak():                                      # Creates a local backup file
    path = askdirectory(title='Select Folder')
    if path != '':
        timestamp = db.time().strftime("%Y-%m-%d_%H-%M-%S")
        f = open(path + "/EWOS_" + timestamp + ".bak", "w")
        
        f.write("You'll see it's all a show, keep 'em laughing as you go. Just remember that the last laugh is on you.\n")

        bakEntries = db.load_data()
        print(bakEntries)
        for toople in bakEntries:
            for col in toople:
                if db.isntBlank(str(col)):
                    bakline = str(col).replace("\n", "\\n")
                    bakline = bakline.replace(",", "•")
                    f.write(bakline)
                f.write(",")
            f.write("\n")

        messagebox.showinfo("Backup created", "EWOS_" + timestamp + ".bak" + "\nCreated in:\n" + path)
        f.close

def restore():                                  # Restore DB contents from prev. created local backup file
    bakFile = askopenfile(mode ='r', filetypes =[('EWOS bak', '*.bak')])
    if not db.isntBlank(str(bakFile)):
        return
    lines=bakFile.readlines()

    if lines[0] != "You'll see it's all a show, keep 'em laughing as you go. Just remember that the last laugh is on you.\n":
        messagebox.showerror("Error", "Not a valid EWOS backup file.")
        return
    else:
        password = simpledialog.askstring("ARE YOU SURE?", "This will delete ALL RECORDS in the database \nand re-populate with the selected data.\nEnter system password if you really want to do this:")
        if auth.authenticate(auth.hash_password(password)) == False: 
            messagebox.showerror("Incorrect Password", "Password is incorrect.")
            return

    db.clear_table("WO")

    for eachline in lines[1:]: 
        words = eachline.split(",")

        name = words[1].replace("•", ",")
        department = words[2]
        signature = words[3]
        ticket_status = words[4]
        urgent_status = words[5]
        date = words[6]
        tempDesc = words[7].replace("\\n","\n") 
        desc = tempDesc.replace("•", ",")
        tempNotes = words[8].replace("\\n","\n") 
        techNotes= tempNotes.replace("•", ",")
        dateCompleted = words[9]

        row_values = [name, department, signature, ticket_status, urgent_status, date, desc, techNotes, dateCompleted]

        db.insert(row_values)
        
    load_data()

def Change_Password():                          # Change system password
    window = Toplevel()
    window.title("Change Password")
    window.grab_set()
    window.focus()

    # Create labels and entry fields for the old and new passwords
    old_password_label = Label(window, text="Old Password:")
    old_password_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    old_password_entry = Entry(window, show="*")
    old_password_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    new_password_label = Label(window, text="New Password:")
    new_password_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    new_password_entry = Entry(window, show="*")
    new_password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    confirm_password_label = Label(window, text="Confirm New Password:")
    confirm_password_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
    confirm_password_entry = Entry(window, show="*")
    confirm_password_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    change_button = Button(window, text="Change Password", command=lambda: auth.change_password(old_password_entry.get(), new_password_entry.get(), confirm_password_entry.get(), window))
    change_button.grid(row=3, column=0, columnspan=2, padx=5, pady=(5, 10))

    window.mainloop()

def depMod_interface():                         # Open interface for adding & removing departments

    def update_options():                   # Destroys & re-creates drop-downs to populate them with new data
        nonlocal cdep_remove
        global dept_entry                    
        new_options = db.load_departments()

        cdep_remove.destroy()
        cdep_remove = ttk.OptionMenu(cdeps, killdep, "Select a Department", *new_options)
        cdep_remove.grid(row=1, column=0, padx=5, pady=(5, 10), sticky="ew")

        dept_entry.destroy()
        dept_entry = ttk.OptionMenu(widgets_frame, depSelection, "Select a Department", *new_options)
        dept_entry.grid(row=3, column=0, padx=5, pady=(0, 5), sticky="ew")

    def add():                              # Add department function
        db.add_department(cdep_add.get())
        cdep_add.delete(0, "end")
        cdep_add.insert(0, "")
        update_options()

    def remove():                           # Remove department function
        db.kill_department(killdep.get())
        update_options()

    deptNames = db.load_departments()

    cdeps = Toplevel()
    cdeps.title("Modify Departments")
    killdep = StringVar()
    killdep.set("Select a Department")
    cdeps.resizable(False,False)
    cdeps.grab_set()
    cdeps.focus()

    cdep_add = ttk.Entry(cdeps, width=30)
    cdep_add.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    cdep_add_button = ttk.Button(cdeps, text="Add", command=add)
    cdep_add_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    cdep_remove = ttk.OptionMenu(cdeps, killdep, "Select a Department", *deptNames)
    cdep_remove.grid(row=1, column=0, padx=5, pady=(5, 10), sticky="ew")

    cdep_remove_label = ttk.Button(cdeps, text="Remove", command=remove)
    cdep_remove_label.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

def editConn():                                 # Edit MySQL connection credentials

    try:
        f = open("connect.cnf", "r")
        conData = f.readlines()
        us = conData[1].replace("user = ", "").strip()
        pw = conData[2].replace("password = ", "").strip()
        hs = conData[3].replace("host = ", "").strip()
        f.close()
    except:
        us = ""
        pw = ""
        hs = ""

    def apply():

        pingResponse = db.ping(modConHost.get(), modConUser.get(), modConPassword.get())

        if pingResponse == False:
            messagebox.showerror("No connection", "Unable to resolve a connection to the WORKORDERS database with those credentials.")
            return

        elif pingResponse == True:
            f = open("connect.cnf", "w")
            f.write("[mysql]\n")
            f.write("user = " + modConUser.get()+"\n")
            f.write("password = " + modConPassword.get() +"\n")
            f.write("host = " + modConHost.get()+"\n")
            f.write("database = WORKORDERS")
            f.close
            global conn_warning
            conn_warning.destroy()

        modConMenu.destroy()

    modConMenu = Toplevel()
    modConMenu.title("Edit Connection")
    modConMenu.resizable(False,False)
    modConMenu.grab_set()
    modConMenu.focus()

    modConUser_l = ttk.Label(modConMenu, text = "User:", anchor="w")
    modConUser_l.grid(row=0, column=0, padx=5, pady=(10,0), sticky="ew")
    modConUser = ttk.Entry(modConMenu, width=30)
    modConUser.insert(0, us)
    modConUser.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    modConPassword_l = ttk.Label(modConMenu, text = "Password:", anchor="w")
    modConPassword_l.grid(row=1, column=0, padx=5, pady=(10,0), sticky="ew")
    modConPassword = ttk.Entry(modConMenu, width=30, show="*")
    modConPassword.insert(0, pw)
    modConPassword.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    modConHost_l = ttk.Label(modConMenu, text = "Host:", anchor="w")
    modConHost_l.grid(row=2, column=0, padx=5, pady=(10,0), sticky="ew")
    modConHost = ttk.Entry(modConMenu, width=30)
    modConHost.insert(0, hs)
    modConHost.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    modCon_button = ttk.Button(modConMenu, text="Connect", command=apply)
    modCon_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    modConMenu.wait_window()


# Check for connectivity with existing MySQL credentials
import configparser
import mysql.connector

def check_conn(config_path='database/connect.cnf') -> bool:
    config = configparser.ConfigParser()
    try:
        config.read(config_path)
        user = config.get('client', 'user')
        password = config.get('client', 'password')
        host = config.get('client', 'host')
        database = config.get('client', 'database', fallback=None)

        conn = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            database=database
        )
        conn.ping(reconnect=True, attempts=3, delay=2)
        conn.close()
        return True
    except Exception as e:
        print(f"Connection check failed: {e}")
        return False


root = Tk()
root.title("Boardwalk Electronic Work Order System")
root.resizable(False,False)
sv_ttk.set_theme("light")

root.iconbitmap(default='bw_guy.ico')
root.bind('<Delete>',lambda event:delete_row())

if check_conn() == False:

    prompt = '''Uh oh!\n
        You'll need to configure
        the server connection to
        use the Boardwalk EWOS!\n
        If things were working before,
        there might be a problem
        with the server. Contact
        your system administrator.'''


    conn_warning = ttk.Label(root, text = prompt, justify="center")
    conn_warning.pack(padx=(10,25), pady=20)
    editConn()

frame = ttk.Frame(root)
frame.pack()

menubar = Menu(root)
datamenu = Menu(menubar, tearoff=0)
datamenu.add_command(label="Create Backup", command=bak)
datamenu.add_command(label="Restore From Backup", command=restore)
datamenu.add_command(label="Modify Departments", command=depMod_interface)
datamenu.add_separator()
datamenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="Data", menu=datamenu)

sysmenu = Menu(menubar, tearoff=0)
sysmenu.add_command(label="Change Password", command=Change_Password)
sysmenu.add_command(label="Connection", command=editConn)
menubar.add_cascade(label="System", menu=sysmenu)
root.config(menu=menubar)

# Label to be used in the LabelFrame since Lframe text cant be styled inline for some dumb reason
Flabel = ttk.Label(text="Submit Work Order", font='bold')

# Insert Form Container
widgets_frame = ttk.LabelFrame(frame, labelwidget=Flabel)
widgets_frame.grid(row=0, column=0, padx=20, pady=10)

# Name Label
name_label = ttk.Label(widgets_frame, text = "Requestor:", anchor="w")
name_label.grid(row=0, column=0, padx=5, pady=(10,0), sticky="ew")
# Name Entry
name_entry = ttk.Entry(widgets_frame)
name_entry.bind("<FocusIn>", lambda e: name_entry.delete('0', 'end'))
name_entry.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="ew")

# Department Label
dept_label = ttk.Label(widgets_frame, text = "Department:", anchor="w")
dept_label.grid(row=2, column=0, padx=5, sticky="ew")
# Department OptionMenu
deptNames = db.load_departments()
depSelection=StringVar()
dept_entry = ttk.OptionMenu(widgets_frame, depSelection, "Select a Department", *deptNames)
dept_entry.grid(row=3, column=0, padx=5, pady=(0, 5), sticky="ew")

# Urgent Checkbox
urgent_checkbox = ttk.Checkbutton(widgets_frame, text="Urgent?", variable=0)
urgent_checkbox.grid(row=4, column=0, padx=5, pady=5, sticky="nsew")

# Description Label
notes_label = ttk.Label(widgets_frame, text = "Issue Description:", anchor="w")
notes_label.grid(row=5, column=0, padx=5, sticky="ew")
# Description Field
notes_entry = Text(widgets_frame, width=35, height=10)
notes_entry.bind("<FocusIn>", lambda e: notes_entry.delete('1.0', 'end'))
notes_entry.grid(row=6, column=0, padx=5, pady=(0,10), sticky="ew")

# Insert Button
Insert_button = ttk.Button(widgets_frame, text="Insert", command=insert_row)
Insert_button.grid(row=7, column=0, padx=5, pady=5, sticky="nsew")

# Delete Button
Delete_button = ttk.Button(widgets_frame, text="Delete", command=delete_row)
Delete_button.grid(row=8, column=0, padx=5, pady=5, sticky="nsew")

# View/Modify Button
ViewMod_button = ttk.Button(widgets_frame, text="View/Modify", command=open_popup)
ViewMod_button.grid(row=9, column=0, padx=5, pady=5, sticky="nsew")

# Separator
separator = ttk.Separator(widgets_frame)
separator.grid(row=10, column=0, padx=(20, 10), pady=10, sticky="ew")

# Theme Switch Button
mode_switch = ttk.Checkbutton(widgets_frame, text="Mode", command=toggle_mode, width=5)
mode_switch.grid(row=11, column=0, padx=5, pady=10, sticky="nsw")

# Filter Button
Filter_button = ttk.Button(widgets_frame, text="Filter", command=filter_popup, width=8)
Filter_button.grid(row=11, column=0, padx=(100,10), pady=10, sticky="nsw")

# Refresh Button
Refresh_button = ttk.Button(widgets_frame, text="Refresh", command=load_data, width=8)
Refresh_button.grid(row=11, column=0, padx=(0,10), pady=10, sticky="nse")


treeFrame = ttk.Frame(frame)
treeFrame.grid(row=0, column=1, pady=10, sticky="ns")
treeScroll = ttk.Scrollbar(treeFrame)
treeScroll.pack(side="right", fill="y")

# Configure Treeview Columns
cols = (" ID", "Requestor", "Dept", "Status", " ", "Requested", "Notes")
treeview = ttk.Treeview(treeFrame, show="headings", yscrollcommand=treeScroll.set, columns=cols) 
treeview.column(" ID", width=30)
treeview.column("Requestor", width=120)
treeview.column("Dept", width=90)
treeview.column("Status", width=70)
treeview.column(" ", width=70)
treeview.column("Requested", width=110)
treeview.column("Notes", width=200)

for col in cols:                        # Gives all column headers basic sort functionality
    treeview.heading(col, text=col, command=lambda c=col: sort_treeview(treeview, c, False))

# Define more specific sorting behavior for ID and Date Requested columns
treeview.heading(' ID', text=' ID', command=lambda: sort_treeview(treeview, ' ID', True))
treeview.heading('Requested', text='Requested', command=lambda: sort_treeview(treeview, 'Requested', True))

for col in cols:                        # Set the anchor for each column explicitly
    treeview.heading(col, text=col, anchor="w")

load_data()                             # Populate treeview with db data
sort_treeview(treeview, ' ID', True)    # Sort most recent tix to top when program is opened

treeview.pack(fill='y', expand=True)
treeScroll.config(command=treeview.yview)


urgent_checkbox.state(['!alternate'])   # these stop the checkboxes from 
mode_switch.state(['!alternate'])       # initially displaying in quantum state

root.mainloop()