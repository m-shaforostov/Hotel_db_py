import tkinter as tk
from tkinter import ttk
import sqlite3


class GUI:
    def __init__(self, hotel):
        self.hotel = hotel
        self.root = tk.Tk()
        self.root.title("Hotel Database")
        self.table = None

        self.create_buttons()
        self.create_table()
        self.fill_the_table("Guests")

        self.root.mainloop()

    def create_buttons(self):
        header_frame = tk.Frame(self.root)
        header_frame.pack(side=tk.TOP)

        tk.Button(header_frame, text="Load Guests", command=self.load_guests).pack(side=tk.LEFT)
        tk.Button(header_frame, text="Load Rooms", command=self.load_rooms).pack(side=tk.LEFT)
        tk.Button(header_frame, text="Load Bookings", command=self.load_bookings).pack(side=tk.LEFT)

    def create_table(self):
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True)

        self.table = ttk.Treeview(table_frame)
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure()  # yscroll=scrollbar.set
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def fill_the_table(self, table):
        self.table["columns"] = self.hotel.get_columns_names(table)
        self.table.column("#0", width=0, stretch=tk.NO)  # Hide the default first column
        self.table.heading("#0", text="", anchor=tk.W)

        for col in self.table["columns"]:
            w = 200
            if col[-2:] == "id":
                w = 100
            self.table.column(col, anchor=tk.W, width=w)
            self.table.heading(col, text=col, anchor=tk.W)

    def load_data(self, table_name, columns):
        # Clear the current table
        # for item in self.table.get_children():
        #     self.table.delete(item)

        # Connect to the database and fetch data
        conn = sqlite3.connect("hotel.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        conn.close()

        # Update the Treeview widget with new columns and data
        self.table["columns"] = columns
        for col in self.table["columns"]:
            self.table.heading(col, text=col)

        for row in rows:
            self.table.insert("", tk.END, values=row)

    def load_guests(self):
        self.load_data("Guests", ("ID", "Name", "Gender", "Age"))

    def load_rooms(self):
        self.load_data("Rooms", (
            "RoomNumber", "BedsType", "PricePerNight", "AvailabilityStatus", "BathroomType", "Balcony",
            "SideOfBuilding"))

    def load_bookings(self):
        self.load_data("Bookings",
                       ("BookingID", "GuestID", "RoomNumber", "CheckInDate", "NightsStayed", "CheckOutDate"))