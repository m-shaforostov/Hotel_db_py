import tkinter as tk
from tkinter import ttk
import sqlite3

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
        self.entry_widgets = []

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
                  command=lambda: ...).pack(side=tk.LEFT)
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
        self.table.configure(yscroll=scrollbar.set)  #
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def draw_columns(self, table):
        self.table["columns"] = self.hotel.get_columns_names(table)
        for col in self.table["columns"]:
            w = 200
            self.table.column(col, anchor=tk.W, width=w)
            self.table.heading(col, text=col, anchor=tk.W)

    def wipe_table_data(self):
        for item in self.table.get_children():
            self.table.delete(item)

    def load_table(self, table):
        if not self.loaded_table:
            self.create_change_buttons()
            self.create_table()
        self.loaded_table = table

        self.wipe_table_data()

        self.table.column("#0", width=0, stretch=tk.NO)  # Hide the default first column
        self.draw_columns(table)

        self.hotel.cursor.execute(f"SELECT * FROM {table}")
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
            updating_data = self.first_selected_data[1:]
            self.edit_window = tk.Toplevel(self.root)
            self.edit_window.transient(self.root)  # Set to be on top of the main window
            self.edit_window.grab_set()  # Make the window modal
            self.edit_window.focus()  # Set focus on the edit window
            for index, value in enumerate(self.first_selected_data[1:]):
                tk.Label(self.edit_window, text=self.table["columns"][index]).grid(row=index, column=0)
                entry = tk.Entry(self.edit_window)
                entry.insert(0, value)
                entry.grid(row=index, column=1)
                self.entry_widgets.append(entry)
            save_button = tk.Button(self.edit_window, text='Save', command=self.update_row_in_db)
            save_button.grid(row=len(updating_data), column=1, sticky='e')
            self.edit_window.bind('<Return>', self.update_row_in_db)
        else:
            print("No row selected")

    def update_row_in_db(self, _=None):
        table = self.loaded_table
        row_id = self.first_selected_data[0]
        new_data_array = [entry.get() or None for entry in self.entry_widgets]
        self.hotel.update_table_row(table, row_id, new_data_array)
        self.load_table(table)
        self.edit_window.destroy()
        print(f"Row {row_id} was updated successfully")
