import sqlite3


class Hotel:
    def __init__(self):
        self.connect = sqlite3.connect('hotel.db')  # Connect to/create
        self.cursor = self.connect.cursor()

        self.create_tables()
        self.console_interface()

        # self.write_table_into_file("Guests", "storage/guests_text_20.dat")
        # self.insert_data_to_table("Guests", ["LLLLL","JJJJJJJ","liam.jackson@example.com","+421-95-162-0414",99])

        self.connect.commit()
        self.connect.close()

    def create_tables(self):
        # Create some tables -------------------------------------------------------------------------------------------
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Guests (
                guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                age INTEGER
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

        # cursor.execute('''
        #     CREATE TABLE IF NOT EXISTS Services (
        #         service_id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         name TEXT NOT NULL,
        #         description TEXT,
        #         price REAL NOT NULL
        #     )
        # ''')

        # --------------------------------------------------------------------------------------------------------------

    def console_interface(self):
        reading_from_files = input("Hello! Before we start, do you want to read data from files? y/[n]\n")
        if reading_from_files.lower() == "y" or reading_from_files == "yes":
            self.load_database_from_files()

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
        return data_array

    def clear_table(self, table):
        self.cursor.execute(f'DELETE FROM {table};')
        self.cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table}"')

    def delete_table(self, table):
        self.cursor.execute(f'DROP TABLE IF EXISTS {table};')

    # TODO
    def update_table_row(self, table, row_id, new_data_array):
        self.cursor.execute(f"UPDATE {table} SET ;")

    def get_columns_names(self, table):
        columns_info = self.cursor.execute(f'PRAGMA table_info({table})').fetchall()
        columns_names = []
        for col in columns_info:
            columns_names.append(col[1])
        return tuple(columns_names)

    def insert_many_rows(self, table, table_data):
        table_columns = self.get_columns_names(table)[1:]
        self.cursor.executemany(f'''
            INSERT INTO {table} {table_columns}
            VALUES ({(len(table_columns) * "?, ")[:-2]})
            ''', table_data)

    def load_database_from_files(self):
        guests_data = self.parse_to_array("storage/guests_text_20.dat")
        rooms_data = self.parse_to_array("storage/rooms_text_20.dat")
        bookings_data = self.parse_to_array("storage/bookings_text_20.dat")
        payments_data = self.parse_to_array("storage/payments_text_20.dat")
        staff_data = self.parse_to_array("storage/staff_text_20.dat")

        self.clear_table("Guests")
        self.insert_many_rows("Guests", guests_data)

        self.clear_table("Rooms")
        self.insert_many_rows("Rooms", rooms_data)

        self.clear_table("Bookings")
        self.insert_many_rows("Bookings", bookings_data)

        self.clear_table("Payments")
        self.insert_many_rows("Payments", payments_data)

        self.clear_table("Staff")
        self.insert_many_rows("Staff", staff_data)

    def write_table_into_file(self, table, file_name):
        self.cursor.execute(f"SELECT * FROM {table}")
        rows = self.cursor.fetchall()
        b_data = b''
        for row in rows:
            b_row = b'\x00'.join([str(element).encode('utf-8') for element in row][1:]) + b'\x00\x00'
            b_data += b_row

        with open(file_name, 'wb') as file:
            file.write(b_data)

    def insert_data_to_table(self, table, data_array):
        table_columns = self.get_columns_names(table)[1:]
        self.connect.execute(
            f'INSERT INTO {table} {table_columns} VALUES ({(len(table_columns) * "?, ")[:-2]})', data_array)



h = Hotel()