import sqlite3
import os
import gui

class Hotel:
    def __init__(self):
        try:
            self.connect = sqlite3.connect('hotel.db')  # Connect to/create
            self.cursor = self.connect.cursor()
            self.create_tables()
            self.load_database_from_files()
            self.g = gui.GUI(self)

            # self.connect.execute(f'INSERT INTO Guests (first_name, last_name, email) VALUES ("Maksym", "Shaforostov", "maxim.sahfrosotov@gmail.com")')
            # self.connect.commit()


            # self.clear_table("Guests")
            # self.remove_row("Guests", 1)
            # self.insert_data_to_table("Bookings", ["7", "103", "2024-07-04", "10", "2024-07-14"])
            # self.update_table_row("Guests", 20, ["Liamm", "Jackson", "liam.jackson@example.com", "+421-95-162-0414"])
            # self.update_table_row("Guests", 19, ["Evelyn", "Martinez", "evelyn.martinez@example.com", None])
            # self.update_table_row("Guests", 18, [None,"Hernandez","abigail.hernandez@example.com","+421-95-867-7175"])

            # self.write_table_into_file("Guests", "storage/guests_text_20.dat")
        except sqlite3.Error as error:
            print(f"Error while working with DB: '{error}'")
        finally:
            if self.connect:
                self.connect.commit()
                self.connect.close()

    # Create some tables ----------------------------------------------------------------------------------------------
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Guests (
                guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone_number TEXT,
                photo BLOB
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Rooms (
                room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number TEXT NOT NULL,
                beds_number INTEGER NOT NULL,
                price_per_night REAL NOT NULL,
                availability_status TEXT NOT NULL,
                bathroom_type TEXT,
                balcony BOOLEAN,
                side_of_building TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_id INTEGER,
                room_id INTEGER,
                check_in_date TEXT NOT NULL,
                nights_number INTEGER NOT NULL,
                check_out_date TEXT NOT NULL,
                FOREIGN KEY (guest_id) REFERENCES Guests (guest_id),
                FOREIGN KEY (room_id) REFERENCES Rooms (room_id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER,
                amount REAL NOT NULL,
                payment_date TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                FOREIGN KEY (booking_id) REFERENCES Bookings (booking_id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Staff (
                staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                position TEXT NOT NULL,
                email TEXT NOT NULL,
                phone_number TEXT NOT NULL
            )
        ''')

    # --------------------------------------------------------------------------------------------------------------
    # Load database ------------------------------------------------------------------------------------------------
    @staticmethod
    def parse_to_array(file_name):
        with open(file_name, "rb") as file:
            data = file.read()
            data_array = []
            for row in data.split(b'\x00\x00')[:-1]:
                row_array = []
                for element in row.split(b'\x00'):
                    el = element.decode()
                    if el.isdigit():
                        el = int(el)
                    row_array.append(el)
                data_array.append(tuple(row_array))
        return data_array[:-1]

    def load_database_from_files(self, file=""):
        try:
            guests_data = self.parse_to_array("storage/guests_data_text.dat")
            rooms_data = self.parse_to_array("storage/rooms_data_text.dat")
            bookings_data = self.parse_to_array("storage/bookings_data_text.dat")
            payments_data = self.parse_to_array("storage/payments_data_text.dat")

            self.clear_table("Guests")
            self.insert_many_rows("Guests", guests_data)

            self.clear_table("Rooms")
            self.insert_many_rows("Rooms", rooms_data)

            self.clear_table("Bookings")
            self.insert_many_rows("Bookings", bookings_data)

            self.clear_table("Payments")
            self.insert_many_rows("Payments", payments_data)

            self.connect.commit()
        except FileNotFoundError as er:
            print(f"File not found: {er.filename}")
        except sqlite3.Error as er:
            print(f"SQLite error: {er}")
        except Exception as er:
            print(f"An unexpected error occurred: {er}")

    @staticmethod
    def convert_to_binary_data(file_name):
        with open(file_name, 'rb') as file:
            blob_data = file.read()
        return blob_data

    def insert_image(self, guest_id, filename):
        binary_data = self.convert_to_binary_data(filename)
        self.cursor.execute("UPDATE Guests SET photo = ? WHERE guest_id = ?", (binary_data, guest_id))
        self.connect.commit()

    @staticmethod
    def write_to_file(data, filename):
        with open(filename, 'wb') as file:
            file.write(data)

    def read_image(self, guest_id, output_filename):
        self.cursor.execute("SELECT photo FROM Guests WHERE guest_id = ?", (guest_id,))
        photo = self.cursor.fetchone()[0]
        if photo:
            self.write_to_file(photo, output_filename)
            return True

    # ------------------------------------------------------------------------------------------------------------------
    # Managing DB ------------------------------------------------------------------------------------------------------
    def get_columns_names(self, table):
        columns_info = self.cursor.execute(f'PRAGMA table_info({table})').fetchall()
        columns_names = []
        for col in columns_info:
            columns_names.append(col[1])
        return tuple(columns_names)

    def clear_table(self, table):
        self.cursor.execute(f'DELETE FROM {table};')
        self.cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table}"')
        self.connect.commit()

    def delete_table(self, table):
        self.cursor.execute(f'DROP TABLE IF EXISTS {table};')
        self.connect.commit()

    @staticmethod
    def delete_database(db):
        if os.path.exists(db):
            os.remove(db)

    def update_table_row(self, table, row_id, new_data_array):
        try:
            table_columns = self.get_columns_names(table)
            id_name = table_columns[0]  # name of the row_id column
            if table == "Guests":
                columns = table_columns[1:-1]  # names of columns without id column and photo
            else:
                columns = table_columns[1:]
            set_query = ", ".join(f'{col} = ?' for col in columns)  # first_name = ?, last_name = ?, ...
            sql = f'UPDATE {table} SET {set_query} WHERE {id_name} = ?;'
            self.cursor.execute(sql, (*new_data_array, row_id))
            self.connect.commit()
        except sqlite3.Error as error:
            raise error

    def insert_many_rows(self, table, table_data):
        try:
            if table == "Guests":
                table_columns = self.get_columns_names(table)[1:-1]
            else:
                table_columns = self.get_columns_names(table)[1:]
            print(table, table_columns, table_data)
            self.cursor.executemany(f'''
                INSERT INTO {table} {table_columns}
                VALUES ({(len(table_columns) * "?, ")[:-2]})
                ''', table_data)
            self.connect.commit()
        except sqlite3.Error as error:
            raise error

    def insert_data_to_table(self, table, data_array):
        try:
            if table == "Guests":
                table_columns = self.get_columns_names(table)[1:-1]
            else:
                table_columns = self.get_columns_names(table)[1:]
            self.connect.execute(
                f'INSERT INTO {table} {table_columns} VALUES ({(len(table_columns) * "?, ")[:-2]})', data_array)
            self.connect.commit()
        except sqlite3.Error as error:
            raise error

    def remove_row(self, table, id):
        try:
            table_columns = self.get_columns_names(table)
            id_name = table_columns[0]  # name of the row_id column
            self.connect.execute(
                f'DELETE FROM {table} WHERE {id_name} = ?', (str(id),))
            self.connect.commit()
        except sqlite3.Error as error:
            print(f"Error while removing a row: '{error}'")

    # ------------------------------------------------------------------------------------------------------------------
    # Saving to files --------------------------------------------------------------------------------------------------
    def write_table_into_file(self, table, file_name):
        self.cursor.execute(f"SELECT * FROM {table}")
        rows = self.cursor.fetchall()
        b_data = b''
        for row in rows:
            b_row = b'\x00'.join([str(element).encode('utf-8') for element in row][1:]) + b'\x00\x00'
            b_data += b_row
    
        with open(file_name, 'wb') as file:
            file.write(b_data)


h = Hotel()