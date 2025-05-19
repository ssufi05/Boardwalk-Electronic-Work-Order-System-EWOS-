import mysql.connector
from mysql.connector import Error
import configparser
from tkinter import messagebox
import tkinter as tk
import humanize
from datetime import datetime
import logging
import logging.handlers
import contextlib

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.handlers.RotatingFileHandler('app.log', maxBytes=2**30, backupCount=3)
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

class WorkOrdersDB:

    def __init__(self):
        self.connection = None
        self.cursor = None

    @contextlib.contextmanager
    def connect(self):
        config = configparser.ConfigParser()
        config.read('database/connect.cnf')

        try:
            self.connection = mysql.connector.connect(
                host=config.get('client', 'host'),
                user=config.get('client', 'user'),
                password=config.get('client', 'password'),
                database=config.get('client', 'database')
            )
            self.cursor = self.connection.cursor()
        except mysql.connector.Error as e:
            logger.error(f"Error while connecting to MySQL  {e}")

    def ping(self, h, us, pw):                                  # This pings user-provided address & credentials to look for WORKORDERS
        try:
            self.connection = mysql.connector.connect(
                host=h,
                user=us,
                password=pw,
                database='WORKORDERS'
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                self.cursor.execute("SHOW DATABASES LIKE 'WORKORDERS'")
                if self.cursor.fetchone():
                    print("Connection successful!")
                    self.connection.close()
                    return True
                else:
                    self.connection.close()
                    return False
        except Error as e:
            print("Connection failed :(", e)
            return False

    def isntBlank(self, checkstring):                           # Checks strings for empty, null, whitespace, etc.
        if checkstring == None or checkstring.isspace() or checkstring =="" or checkstring == "Empty" or checkstring == "None":
            return False
        
        return True

    def insert_age_format(self, tv, rows):                      # Inserts tickets to the treeview with human-readable age strings
        for each_row in rows:
            i=0
            age_formatted_row = []
            for col in each_row:
                if i != 3 and i <= 7:
                    try:
                        col_str = str(col)  # Convert col to string
                        coldate = datetime.strptime(col_str, "%Y-%m-%d %H:%M:%S")
                        delta = datetime.now() - coldate
                        age = humanize.naturaltime(delta)
                        age_formatted_row.append(age)
                    except ValueError:
                        age_formatted_row.append(col_str)
                i = i + 1
            tv.insert('', tk.END, values=tuple(age_formatted_row))

    def load_data(self):                                        # Returns a list of entries in the WO table
        try:
            self.connect()
            sql_select_query = """SELECT id, name, department, signature, ticket_status, urgent_status, date, notes, tech_notes, complete_date FROM WO"""
            cursor = self.connection.cursor()
            cursor.execute(sql_select_query)
            records = cursor.fetchall()
            list_values = list(records)
            return list_values
        except mysql.connector.Error as error:
                messagebox.showerror("Error", str(error))
                logger.error(f"Error while loading data: {error}")

    def time(self):                                             # Returns the system time on the server machine

        try:
            self.connect()
            self.cursor.execute("SELECT CURRENT_TIMESTAMP()")
            now = self.cursor.fetchone()[0]
            return now
        
        except Error as e:
            self.connection.rollback()
            logger.error(f"Error while querying server for time: {e}")

    def insert(self, data):                                     # Inserts a ticket as a WO table row

        sql = """
        INSERT INTO WO (`name`, `department`, `signature`, `ticket_status`, `urgent_status`, `date`, `notes`, `tech_notes`, `complete_date`) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.connect()
            self.cursor.execute(sql, data)
            self.connection.commit()
            print(self.cursor.rowcount, "record(s) inserted successfully.")
        except Error as e:
            self.connection.rollback()
            logger.error(f"Error while inserting data: {e}")

    def clear_table(self, table_name):                          # Clears the called table
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(f"TRUNCATE TABLE {table_name}")
            self.connection.commit()
        except Error as e:
            self.connection.rollback()
            logger.error(f"Error while clearing data: {e}")

    def delete_item(self, id):                                  # Deletes a row with the given ID from the WO table
        sql = "DELETE FROM WO WHERE id = %s"
        print(id)
        try:
            self.connect()
            row = self.get_row_by_id(id)
            self.cursor.execute(sql, (id,))
            self.connection.commit()
            logger.info(f"Record with ID {id} deleted successfully. Row data: {row}")
        except Error as e:
            self.connection.rollback()
            logger.error(f"Error while deleting data: {e}")

    def update_item(self, new_values):                          # Modifies the values in a WO table row
        query = "UPDATE WO SET name=%s, department=%s, ticket_status=%s, urgent_status=%s, notes=%s, tech_notes=%s WHERE id=%s"
        try:
            self.connect()
            self.cursor.execute(query, new_values)
            self.connection.commit()
            logger.info(f"Record with ID {new_values[6]} updated: {new_values}")
        except Error as e:
            self.connection.rollback()
            logger.error(f"Error while modifying data: {e}")

    def sign(self, techsig, id):                                # Adds data to the `signature` col in a WO table row
        query = "UPDATE WO SET signature=%s WHERE id=%s"
        try:
            self.connect()
            self.cursor.execute(query, (techsig, id))
            self.connection.commit()
        except Error as e:
            self.connection.rollback()
            logger.error(f"Error while signing form: {e}")

    def insert_completion_date(self, date, id):                 # Adds data to the `complete_date` col in a WO table row
        query = "UPDATE WO SET complete_date=%s WHERE id=%s"
        try:
            self.connect()
            self.cursor.execute(query, (date, id))
            self.connection.commit()
        except Error as e:
            self.connection.rollback()
            logger.error(f"Error while dating form: {e}")

    def load_departments(self):                                 # Returns a list of departments in the `departments` table
        try:
            self.connect()
            sql_select_query = """SELECT * FROM departments"""
            cursor = self.connection.cursor()
            cursor.execute(sql_select_query)
            records = cursor.fetchall()

            department_names = [record[0] for record in records] #convert from tuples into a list of strings

            return department_names
        except mysql.connector.Error as error:
            messagebox.showerror("Error", str(error))
            logger.error(f"Error while loading departments: {error}")

    def get_row_by_id(self, id):                                # Returns a list containing a single WO table entry with the given ID
        query = "SELECT * FROM WO WHERE id = %s"
        try:
            self.connect()
            self.cursor.execute(query, (id,))
            row = self.cursor.fetchall()
            list_row = list(row)
            return list_row
        except Error as e:
            self.connection.rollback()
            logger.error(f"Error while loading row: {e}")

    def add_department(self, dept):                             # Adds a row to the `departments` table
        if self.isntBlank(dept):
            try:
                self.connect()
                cursor = self.connection.cursor()
                add_dep_query = "INSERT INTO departments (`department`) VALUES (%s)"
                cursor.execute(add_dep_query, (dept,))
                self.connection.commit()
            except mysql.connector.Error as error:
                logger.error(f"Error adding department: {error}")

    def kill_department(self, dept):                            # Removes a row from the `departments` table
        if dept != "Select a Department":
            try:
                self.connect()
                cursor = self.connection.cursor()
                remove_dep_query = "DELETE FROM departments WHERE department = %s"
                cursor.execute(remove_dep_query, (dept,))
                self.connection.commit()
            except mysql.connector.Error as error:
                logger.error(f"Error removing department: {error}")

    def close(self):                                            # Closes the connection
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()