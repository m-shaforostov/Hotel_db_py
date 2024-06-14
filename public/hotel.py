import sqlite3


class Hotel:
    def __init__(self):
        self.connect = sqlite3.connect('hotel.db')  # Connect to/create
        self.cursor = self.connect.cursor()

        self.create_tables()
        self.console_interface()

        # self.write_table_into_file("Guests", "storage/guests_text_20.dat")
        # self.insert_data("Guests", ["LLLLL","JJJJJJJ","liam.jackson@example.com","+421-95-162-0414",99])

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
            self.load_data_from_files()


    def parse_to_array(self, file_name):
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

    def truncate_table(self, table):
        self.cursor.execute(f'DELETE FROM {table};')
        self.cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table}"')

    def load_data_from_files(self):
        guests_data = self.parse_to_array("storage/guests_text_20.dat")
        rooms_data = self.parse_to_array("storage/rooms_text_20.dat")
        bookings_data = self.parse_to_array("storage/bookings_text_20.dat")
        payments_data = self.parse_to_array("storage/payments_text_20.dat")
        staff_data = self.parse_to_array("storage/staff_text_20.dat")

        self.truncate_table("Guests")
        self.cursor.executemany('''
        INSERT INTO Guests (first_name, last_name, email, phone_number, age)
        VALUES (?, ?, ?, ?, ?)
        ''', guests_data)

        self.truncate_table("Rooms")
        self.cursor.executemany('''
        INSERT INTO Rooms (room_number, beds_number, price_per_night, availability_status, bathroom_type, balcony, 
            side_of_building)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', rooms_data)

        self.truncate_table("Bookings")
        self.cursor.executemany('''
        INSERT INTO Bookings (guest_id, room_id, check_in_date, nights_number, check_out_date)
        VALUES (?, ?, ?, ?, ?)
        ''', bookings_data)

        self.truncate_table("Payments")
        self.cursor.executemany('''
        INSERT INTO Payments (booking_id, amount, payment_date, payment_method)
        VALUES (?, ?, ?, ?)
        ''', payments_data)

        self.truncate_table("Staff")
        self.cursor.executemany('''
        INSERT INTO Staff (first_name, last_name, position, email, phone_number)
        VALUES (?, ?, ?, ?, ?)
        ''', staff_data)

    def write_table_into_file(self, table, file_name):
        self.cursor.execute(f"SELECT * FROM {table}")
        rows = self.cursor.fetchall()
        b_data = b''
        for row in rows:
            b_row = b'\x00'.join([str(element).encode('utf-8') for element in row][1:]) + b'\x00\x00'
            b_data += b_row

        with open(file_name, 'wb') as file:
            file.write(b_data)

    def insert_data(self, tabel, data_array):
        table_columns = {
            "Guests": "(first_name, last_name, email, phone_number, age)",
            "Rooms": "(room_number, beds_number, price_per_night, availability_status, bathroom_type, balcony, "
                     "side_of_building)",
            "Bookings": "(guest_id, room_id, check_in_date, nights_number, check_out_date)",
            "Payments": "(booking_id, amount, payment_date, payment_method)",
            "Staff": "(first_name, last_name, position, email, phone_number)",
        }
        self.connect.execute(
            f'INSERT INTO {tabel} {table_columns[tabel]} VALUES ({(len(data_array) * "?, ")[:-2]})', data_array)



h = Hotel()