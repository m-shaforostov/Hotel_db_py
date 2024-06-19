import tkinter as tk
from tkinter import ttk
import sqlite3
import re

class GUI:
    def __init__(self, hotel):
        self.hotel = hotel
        self.root = tk.Tk()
        # self.root.geometry('1000x400')
        self.root.title("Hotel Database")

        self.table = None
        self.loaded_table = None
        self.selected_rows = tuple()
        self.first_selected_data = None
        self.edit_window = None
        self.add_window = None
        self.entry_widgets = []
        self.sort_order = dict()

        self.create_open_buttons()

        self.root.mainloop()

    def create_open_buttons(self):
        open_btns_frame = tk.Frame(self.root)
        open_btns_frame.pack(side=tk.TOP)

        tk.Button(open_btns_frame, text="Open Guests", command=lambda: self.load_table("Guests")).pack(side=tk.LEFT)
        tk.Button(open_btns_frame, text="Open Rooms", command=lambda: self.load_table("Rooms")).pack(side=tk.LEFT)
        tk.Button(open_btns_frame, text="Open Bookings", command=lambda: self.load_table("Bookings")).pack(side=tk.LEFT)
        tk.Button(open_btns_frame, text="Open Payments", command=lambda: self.load_table("Payments")).pack(side=tk.LEFT)

    def create_change_buttons(self):
        change_btns_frame = tk.Frame(self.root)
        change_btns_frame.pack(side=tk.TOP)

        tk.Button(change_btns_frame, text="Clear table",
                  command=lambda: self.clear_tabel()).pack(side=tk.LEFT)
        tk.Button(change_btns_frame, text="Remove row",
                  command=lambda: self.delete_items()).pack(side=tk.LEFT)
        tk.Button(change_btns_frame, text="Add row",
                  command=lambda: self.add_row()).pack(side=tk.LEFT)
        tk.Button(change_btns_frame, text="Update row",
                  command=lambda: self.make_row_editable()).pack(side=tk.LEFT)
        tk.Button(change_btns_frame, text="Load DB",
                  command=lambda: self.load_database()).pack(side=tk.LEFT)

    def create_table(self):
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True)

        self.table = ttk.Treeview(table_frame)
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.table.bind('<<TreeviewSelect>>', self.on_row_selected)
        self.table.bind('<Delete>', self.delete_items)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def draw_columns(self, table):
        self.table["columns"] = self.hotel.get_columns_names(table)
        for i, col in enumerate(self.table["columns"]):
            w = 200
            self.table.column(col, anchor=tk.W, width=w)
            heading_text = col
            if col in self.sort_order:
                if self.sort_order[col] == "ASC":
                    heading_text += " ^"
                elif self.sort_order[col] == "DESC":
                    heading_text += " v"
            self.table.heading(col, text=heading_text, anchor=tk.W, command=lambda _col=col: self.sort_by_column(_col))

    def wipe_table_data(self):
        for item in self.table.get_children():
            self.table.delete(item)

    def load_table(self, table):
        if not self.loaded_table:
            self.create_change_buttons()
            self.create_table()
        self.loaded_table = table

        self.wipe_table_data()

        self.table.column("#0", width=0, stretch=tk.NO)  # Hide the first column
        self.draw_columns(table)

        sorting_cols = list()
        for col, ord in self.sort_order.items():
            if ord is not None:
                sorting_cols.append((col, ord))

        if sorting_cols:
            query = ""
            for el in sorting_cols:
                query += f"{el[0]} {el[1]}, "
            print(f"SELECT * FROM {self.loaded_table} ORDER BY {query[:-2]}")
            self.hotel.cursor.execute(f"SELECT * FROM {self.loaded_table} ORDER BY {query[:-2]}")
        else:
            self.hotel.cursor.execute(f"SELECT * FROM {self.loaded_table}")
        rows = self.hotel.cursor.fetchall()
        for row in rows:
            self.table.insert("", tk.END, values=row)

    # ------------------------------------------------------------------------------------------------------------------
    def clear_tabel(self):
        self.hotel.clear_table(self.loaded_table)
        self.wipe_table_data()
        print(f"Table {self.loaded_table} was cleared successfully")

    def load_database(self):
        self.hotel.load_database_from_files()
        self.load_table(self.loaded_table)
        print("Database was loaded successfully")

    def get_row(self, i):
        return str(self.table.item(i)['values'][0])

    def delete_items(self, _=None):
        if self.table.selection():
            for row in self.table.selection():
                self.hotel.remove_row(self.loaded_table, (self.get_row(row),))
                print(f"Row {self.get_row(row)} from {self.loaded_table} was deleted successfully")
            self.load_table(self.loaded_table)
            print()
        else:
            print("No row selected")

    def on_row_selected(self, _):
        self.selected_rows = self.table.selection()
        if self.selected_rows:
            self.first_selected_data = self.table.item(self.selected_rows[0])['values']
            for row in self.selected_rows:
                print(f"Selected row data from {self.loaded_table}: {self.table.item(row)['values']}")
            print()

    def make_row_editable(self):
        if len(self.selected_rows) > 1:
            print("Only one row should be selected")
        elif len(self.selected_rows) == 1:
            self.edit_window = tk.Toplevel(self.root)
            self.edit_window.title("Edit mode")
            self.edit_window.transient(self.root)  # Set to be on top of the main window
            self.edit_window.grab_set()  # Make the window modal
            self.edit_window.focus()  # Set focus on the edit window

            self.entry_widgets = []
            for index, value in enumerate(self.first_selected_data[1:]):  # without id column
                tk.Label(self.edit_window, text=self.table["columns"][index+1]).grid(row=index, column=0)
                entry = tk.Entry(self.edit_window)
                entry.insert(0, value)
                entry.grid(row=index, column=1)
                self.entry_widgets.append(entry)
                if self.table["columns"][index + 1] == "phone_number":
                    print(self.table["columns"][index + 1])

                    entry.bind('<KeyRelease>', lambda event: self.format_phone_number(entry))

            save_button = tk.Button(self.edit_window, text='Save', command=self.update_row_in_db)
            save_button.grid(row=len(self.entry_widgets), column=1, sticky='e')
            self.edit_window.bind('<Return>', self.update_row_in_db)
        else:
            print("No row selected")

    def update_row_in_db(self, _=None):
        try:
            table = self.loaded_table
            row_id = self.first_selected_data[0]
            new_data_array = [entry.get() or None for entry in self.entry_widgets]
            if table == "Guests":
                name_check = self.validate_name(new_data_array[0])
                surname_check = self.validate_name(new_data_array[1], "Surname")
                email_check = self.validate_email(new_data_array[2])
                phone_check = self.validate_phone(new_data_array[3])
                acception = name_check and surname_check and email_check and phone_check
            else:
                acception = True
            if not acception:
                return
            self.hotel.update_table_row(table, row_id, new_data_array)
            self.load_table(table)
            self.edit_window.destroy()
            print(f"Row {row_id} was updated successfully")
        except sqlite3.Error as error:
            print(f"Error while updating a row: '{error}'")

    def add_row(self):
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Add mode")
        self.add_window.transient(self.root)  # Set to be on top of the main window
        self.add_window.grab_set()  # Make the window modal
        self.add_window.focus()  # Set focus on the add window

        self.entry_widgets = []
        for index, col in enumerate(self.table["columns"][1:]):  # without id column
            tk.Label(self.add_window, text=col).grid(row=index, column=0)
            entry = tk.Entry(self.add_window)
            entry.grid(row=index, column=1)
            self.entry_widgets.append(entry)
            if col == "phone_number":
                entry.bind('<KeyRelease>', lambda event: self.format_phone_number(entry))

        add_button = tk.Button(self.add_window, text='Save', command=self.add_row_into_db)
        add_button.grid(row=len(self.entry_widgets), column=1, sticky='e')
        self.add_window.bind('<Return>', self.add_row_into_db)

    def add_row_into_db(self, _=None):
        try:
            table = self.loaded_table
            data_array = [entry.get() or None for entry in self.entry_widgets]
            if table == "Guests":
                name_check = self.validate_name(data_array[0])
                surname_check = self.validate_name(data_array[1], "Surname")
                email_check = self.validate_email(data_array[2])
                phone_check = self.validate_phone(data_array[3])
                acception = name_check and surname_check and email_check and phone_check
            else:
                acception = True
            if not acception:
                return
            self.hotel.insert_data_to_table(table, data_array)
            self.load_table(table)
            self.add_window.destroy()
            print(f"Row was added successfully")
        except sqlite3.Error as error:
            print(f"Error while adding a row: '{error}'")

    @staticmethod
    def format_phone_number(entry):
        text = entry.get()
        text = ''.join(filter(str.isdigit, text))
        # +000-0-000-0000
        if len(text) == 1:
            formatted_text = '+' + text
        else:
            formatted_text = ''

        if len(text) > 1:
            formatted_text += '+' + text[:3]
        if len(text) > 3:
            formatted_text += '-' + text[3:5]
        if len(text) > 5:
            formatted_text += '-' + text[5:8]
        if len(text) > 8:
            formatted_text += '-' + text[8:12]

        entry.delete(0, tk.END)
        entry.insert(0, formatted_text)

    @staticmethod
    def validate_name(name, text="Name"):
        if name is None or len(name) < 2:
            print(text + " should contain at least 2 characters")
            return False
        if any(char.isdigit() for char in name):
            print(text + " should not contain digits")
            return False
        return True

    @staticmethod
    def validate_email(email):
        regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if email is None or not re.match(regex, email):
            print("Invalid email address.")
            return False
        return True

    @staticmethod
    def validate_phone(phone):
        if phone == "":
            return True
        regex = r'^\+\d{3}-\d{2}-\d{3}-\d{4}$'
        if phone is None or not re.match(regex, phone):
            print("Phone number must be in the format +000-00-000-0000")
            return False
        return True

    def sort_by_column(self, col):
        if col not in self.sort_order or self.sort_order[col] is None:
            self.sort_order[col] = "DESC"
        elif self.sort_order[col] == "DESC":
            self.sort_order[col] = "ASC"
        else:
            self.sort_order[col] = None

        self.load_table(self.loaded_table)
