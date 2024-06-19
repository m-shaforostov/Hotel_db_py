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
                  command=lambda: self.load_table("Bookings")).pack(side=tk.LEFT)
        tk.Button(change_btns_frame, text="Load DB",
                  command=lambda: self.load_database()).pack(side=tk.LEFT)

    def create_table(self):
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True)

        self.table = ttk.Treeview(table_frame)
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # self.table.bind('<<TreeviewSelect>>', self.get_rows)
        self.table.bind('<Delete>', self.delete_items)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)  #
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def draw_columns(self, table):
        self.table["columns"] = self.hotel.get_columns_names(table)
        for col in self.table["columns"]:
            w = 200
            # if col.endswith("id"):
            #     w = 50
            # print(w)
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

    def load_database(self):
        self.hotel.load_database_from_files()
        self.load_table(self.loaded_table)

    def get_row(self, i):
        return str(self.table.item(i)['values'][0])

    def delete_items(self, _=None):
        ids = [[self.get_row(row)] for row in self.table.selection()]  # ids = [["2"],["3"]]
        self.hotel.remove_row(self.loaded_table, ids)
        self.load_table(self.loaded_table)