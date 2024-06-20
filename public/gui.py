import tkinter as tk
from tkinter import ttk
import sqlite3
import re
import tkinter.filedialog as fd


class GUI:
    def __init__(self, hotel):
        self.hotel = hotel
        self.root = tk.Tk()
        # self.root.geometry('1000x400')
        self.root.title("Hotel Database")

        self.search_entry = None
        self.table = None
        self.loaded_table = None
        self.selected_rows = tuple()
        self.first_selected_data = None
        self.edit_window = None
        self.add_window = None
        self.errors_window = None
        self.entry_widgets = []
        self.sort_order = dict()
        self.image_buttons = dict()
        self.images = {}

        self.create_open_buttons()

        self.root.mainloop()

    def create_open_buttons(self):
        open_btns_frame = tk.Frame(self.root)
        open_btns_frame.pack(side=tk.TOP)

        tk.Button(open_btns_frame, text="Open Guests", command=lambda: self.load_table("Guests")).pack(side=tk.LEFT)
        tk.Button(open_btns_frame, text="Open Rooms", command=lambda: self.load_table("Rooms")).pack(side=tk.LEFT)
        tk.Button(open_btns_frame, text="Open Bookings", command=lambda: self.load_table("Bookings")).pack(side=tk.LEFT)
        tk.Button(open_btns_frame, text="Open Payments", command=lambda: self.load_table("Payments")).pack(side=tk.LEFT)

    def create_search(self):
        search_frame = tk.Frame(self.root)
        search_frame.pack(side=tk.TOP)

        label = tk.Label(search_frame, text="SQL conditions")
        label.pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT)
        self.add_placeholder(self.search_entry, "gues_id > 1 AND guest_id < 50", label)

        tk.Button(search_frame, text="Execute", command=lambda: self.handle_search()).pack(side=tk.LEFT)
        tk.Button(search_frame, text="Clear", command=lambda: self.clear_conditions()).pack(side=tk.LEFT)
        self.search_entry.bind('<Return>', self.handle_search)

    def handle_search(self, _=None):
        conditions = self.search_entry.get()
        self.load_table(self.loaded_table, conditions)

    def clear_conditions(self):
        self.search_entry.delete(0, tk.END)

    def add_placeholder(self, entry, placeholder, label, color='grey'):
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg='black')

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=color)

        entry.insert(0, placeholder)
        entry.config(fg=color)
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        label.bind("<Button-1>", self.focus_out)

    def focus_out(self, event):
        event.widget.master.focus_set()

    def create_image_buttons(self):
        image_btns_frame = tk.Frame(self.root)
        image_btns_frame.pack(side=tk.TOP)

        self.image_buttons["upload"] = tk.Button(image_btns_frame, text="Upload Image", command=self.upload_image)
        self.image_buttons["display"] = tk.Button(image_btns_frame, text="Display Image", command=self.display_image)
        self.image_buttons["upload"].pack(side=tk.LEFT)
        self.image_buttons["display"].pack(side=tk.LEFT)

    def disable_buttons(self):
        for button in self.image_buttons.values():
            button.config(state=tk.DISABLED)

    def enable_buttons(self):
        for button in self.image_buttons.values():
            button.config(state=tk.NORMAL)

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

    def load_table(self, table, conditions=""):
        if not self.loaded_table:
            self.create_image_buttons()
            self.create_change_buttons()
            self.create_search()
            self.create_table()
        if table != self.loaded_table:
            self.sort_order = dict()
            self.loaded_table = table

        self.wipe_table_data()

        self.table.column("#0", width=0, stretch=tk.NO)  # Hide the first column
        self.draw_columns(table)

        sorted_cols = list()
        for col, ord in self.sort_order.items():
            if ord is not None:
                sorted_cols.append((col, ord))

        query = f"SELECT * FROM {self.loaded_table}"
        sql_ordering = ""

        if conditions:
            query += " WHERE " + conditions

        if sorted_cols:
            sql_ordering = " ORDER BY " + ", ".join([f"{col} {ord}" for col, ord in sorted_cols])

        sql_query = query + sql_ordering
        if conditions:
            print(sql_query)
        try:
            self.hotel.cursor.execute(sql_query)
        except sqlite3.Error as error:
            self.show_errors([error], self.table)
            print(f"Error while searching: '{error}'")

        rows = self.hotel.cursor.fetchall()
        if table == "Guests":
            self.enable_buttons()
            for row in rows:
                row_data = list(row)
                if row_data[-1]:  # photo column
                    row_data[-1] = "picture"
                else:
                    row_data[-1] = "None"
                self.table.insert("", tk.END, values=row_data)
        else:
            self.disable_buttons()
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
                self.hotel.remove_row(self.loaded_table, self.get_row(row))
                print(f"Row {self.get_row(row)} from {self.loaded_table} was deleted successfully")
            self.load_table(self.loaded_table)
            print()
        else:
            self.show_errors(["No row selected"], self.root)
            print("No row selected")

    def on_row_selected(self, _):
        self.selected_rows = self.table.selection()
        if self.selected_rows:
            self.first_selected_data = self.table.item(self.selected_rows[0])['values']
            for row in self.selected_rows:
                print(f"Selected row data from {self.loaded_table}: {self.table.item(row)['values']}")
            print()

    # ------------------------------------------------------------------------------------------------------------------
    def make_row_editable(self):
        if len(self.selected_rows) > 1:
            self.show_errors(["Only one row should be selected"], self.root)
            print("Only one row should be selected")
        elif len(self.selected_rows) == 1:
            self.edit_window = tk.Toplevel(self.root)
            self.edit_window.title("Edit mode")
            self.edit_window.transient(self.root)  # Set to be on top of the main window
            self.edit_window.grab_set()  # Make the window modal
            self.edit_window.focus()  # Set focus on the edit window

            self.entry_widgets = []
            if self.loaded_table == "Guests":
                columns = self.first_selected_data[1:-1]  # without id column and photo
            else:
                columns = self.first_selected_data[1:]
            for index, value in enumerate(columns):
                tk.Label(self.edit_window, text=self.table["columns"][index + 1]).grid(row=index, column=0)
                entry = tk.Entry(self.edit_window)
                entry.insert(0, value)
                entry.grid(row=index, column=1)
                self.entry_widgets.append(entry)
                if self.table["columns"][index + 1] == "phone_number":
                    entry.bind('<KeyRelease>', lambda event: self.format_phone_number(entry))

            save_button = tk.Button(self.edit_window, text='Save', command=self.update_row_in_db)
            save_button.grid(row=len(self.entry_widgets), column=1, sticky='e')
            self.edit_window.bind('<Return>', self.update_row_in_db)
        else:
            self.show_errors(["No row selected"], self.root)
            print("No row selected")

    def update_row_in_db(self, _=None):
        try:
            table = self.loaded_table
            row_id = self.first_selected_data[0]
            new_data_array = [entry.get() or None for entry in self.entry_widgets]
            if table == "Guests":
                errs = [self.validate_name(new_data_array[0]), self.validate_name(new_data_array[1], "Surname"),
                        self.validate_email(new_data_array[2]), self.validate_phone(new_data_array[3])]
                errs = list(filter(str, errs))
                if errs:
                    self.show_errors(errs, self.edit_window)
                    return
            self.hotel.update_table_row(table, row_id, new_data_array)
            self.load_table(table)
            self.edit_window.destroy()
            print(f"Row {row_id} was updated successfully")
        except sqlite3.Error as error:
            self.show_errors([error], self.add_window)
            print(f"Error while updating a row: '{error}'")

    # ------------------------------------------------------------------------------------------------------------------
    def add_row(self):
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Add mode")
        self.add_window.transient(self.root)  # Set to be on top of the main window
        self.add_window.grab_set()  # Make the window modal
        self.add_window.focus()  # Set focus on the add window

        self.entry_widgets = []
        if self.loaded_table == "Guests":
            columns = self.table["columns"][1:-1]
        else:
            columns = self.table["columns"][1:]
        for index, col in enumerate(columns):  # without id column
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
                errs = [self.validate_name(data_array[0]), self.validate_name(data_array[1], "Surname"),
                        self.validate_email(data_array[2]), self.validate_phone(data_array[3])]
                errs = list(filter(str, errs))
                if errs:
                    self.show_errors(errs, self.add_window)
                    return
            self.hotel.insert_data_to_table(table, data_array)
            self.load_table(table)
            self.add_window.destroy()
            print(f"Row was added successfully")
        except sqlite3.Error as error:
            self.show_errors([error], self.add_window)
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
            err = text + " should contain at least 2 characters"
            return err
        if any(char.isdigit() for char in name):
            err = text + " should not contain digits"
            return err
        return ""

    @staticmethod
    def validate_email(email):
        regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if email is None or not re.match(regex, email):
            err = "Invalid email address"
            return err
        return ""

    @staticmethod
    def validate_phone(phone):
        if phone is None:
            return ""
        regex = r'^\+\d{3}-\d{2}-\d{3}-\d{4}$'
        if phone is None or not re.match(regex, phone):
            err = "Phone number must be in the format +000-00-000-0000"
            return err
        return ""

    def show_errors(self, errors, window):
        self.errors_window = tk.Toplevel(self.root)
        self.errors_window.title("Input Error")
        self.errors_window.transient(window)  # Set to be on top of the main window
        self.errors_window.grab_set()  # Make the window modal
        self.errors_window.focus()  # Set focus on the add window
        for err in errors:
            print(err)
            tk.Label(self.errors_window, text=err, fg='red').pack(side=tk.TOP)

    # ------------------------------------------------------------------------------------------------------------------
    def sort_by_column(self, col):
        if col not in self.sort_order or self.sort_order[col] is None:
            self.sort_order[col] = "DESC"
        elif self.sort_order[col] == "DESC":
            self.sort_order[col] = "ASC"
        else:
            self.sort_order[col] = None

        self.load_table(self.loaded_table)

    def upload_image(self):
        try:
            if len(self.selected_rows) > 1:
                self.show_errors(["Only one row should be selected"], self.root)
                print("Only one row should be selected")
            elif len(self.selected_rows) == 1:
                filetypes = (("PNG files", "*.png"), ("All files", "*.*"))
                filename = fd.askopenfilename(title="Open an image",
                                              initialdir="/home/PycharmProjects/Hotel_DB/public/",
                                              filetypes=filetypes)
                row_id = self.table.selection()[0]
                guest_id = self.get_row(row_id)
                self.hotel.insert_image(guest_id, filename)
                self.load_table(self.loaded_table)
            else:
                self.show_errors(["No row selected"], self.root)
                print("No row selected")
        except Exception as err:
            self.show_errors([err], self.root)
            print(err)

    def display_image(self):
        try:
            if len(self.selected_rows) > 1:
                self.show_errors(["Only one row should be selected"], self.root)
                print("Only one row should be selected")
            elif len(self.selected_rows) == 1:
                row_id = self.table.selection()[0]
                guest_id = self.get_row(row_id)
                display_file = "./storage/img/display.png"
                is_picture = self.hotel.read_image(guest_id, display_file)
                if is_picture:
                    image_window = tk.Toplevel(self.root)
                    image_window.transient(self.root)  # Set to be on top of the main window
                    image_window.grab_set()  # Make the window modal
                    image_window.focus()  # Set focus on the add window
                    image = tk.PhotoImage(file=display_file)
                    label = tk.Label(image_window, image=image)
                    label.image = image
                    label.pack()
                else:
                    self.show_errors(["There is no picture stored"], self.root)
                    print("There is no picture stored")
            else:
                self.show_errors(["No row selected"], self.root)
                print("No row selected")
        except Exception as err:
            self.show_errors([err], self.root)
            print(err)
