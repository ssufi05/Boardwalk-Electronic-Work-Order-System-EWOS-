import hashlib
from database.database_connector import WorkOrdersDB
import mysql.connector
from tkinter import messagebox

db = WorkOrdersDB()

class Authenticate:
    def __init__(self):
        self.connection = None

    def hash_password(self, password):
        salt = "my_salt"
        return hashlib.sha256(salt.encode() + password.encode()).hexdigest()

    def authenticate(self, username, password):
        db.connect()
        cursor = db.connection.cursor()
        query = "SELECT password FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        db.close()

        if not result:
            return False  # User not found

        stored_password = result[0]
        hashed_input_password = self.hash_password(password)

        return hashed_input_password == stored_password

    def register(self, username, password):
        db.connect()
        cursor = db.connection.cursor()
        hashed_password = self.hash_password(password)
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, hashed_password))
        db.connection.commit()
        db.close()

    def change_password(self, username, old_password, new_password, confirm_password, window):
        # Check if the old password is correct
        if not self.authenticate(username, old_password):
            messagebox.showerror("Incorrect Password", "The old password is incorrect.")
            return

        # Check if the new password and confirmed password match
        if new_password != confirm_password:
            messagebox.showerror("Password Mismatch", "The new password and confirmed password do not match.")
            return

        # Hash the new password
        hashed_new_password = self.hash_password(new_password)

        try:
            db.connect()
            cursor = db.connection.cursor()
            query = "UPDATE users SET password = %s WHERE username = %s"
            cursor.execute(query, (hashed_new_password, username))
            db.connection.commit()
            window.destroy()
        except mysql.connector.Error as error:
            print("Error", str(error))
        finally:
            db.close()

        messagebox.showinfo("Password Changed", "Your password has been changed successfully.")
