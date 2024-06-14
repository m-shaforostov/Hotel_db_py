import sqlite3


class Hotel:
    def __init__(self):
        self.connection = sqlite3.connect('hotel.db')  # Connect to/create
        self.cursor = self.connection.cursor()

        self.create_tables()
        self.insert_data()

        self.connection.commit()
        self.connection.close()

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

    def insert_data(self):

        # with open("backup/guests_text_20", "r", encoding="utf-8") as file:
        #     guests_data = []
        #     for row in file.read().split("\n"):
        #         row_tuple = []
        #         for element in row.split(";"):
        #             if element.isdigit():
        #                 element = int(element)
        #             row_tuple.append(element)
        #         guests_data.append(tuple(row_tuple))

        guests_data = self.parse_to_array("storage/guests_text_20.dat")
        print(guests_data)
        rooms_data = self.parse_to_array("storage/rooms_text_20.dat")
        bookings_data = self.parse_to_array("storage/bookings_text_20.dat")
        payments_data = self.parse_to_array("storage/payments_text_20.dat")
        staff_data = self.parse_to_array("storage/staff_text_20.dat")

        self.cursor.executemany('''
        INSERT INTO Guests (first_name, last_name, email, phone_number, age)
        VALUES (?, ?, ?, ?, ?)
        ''', guests_data)

        self.cursor.executemany('''
        INSERT INTO Rooms (room_number, beds_number, price_per_night, availability_status, bathroom_type, balcony, side_of_building)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', rooms_data)

        self.cursor.executemany('''
        INSERT INTO Bookings (guest_id, room_id, check_in_date, nights_number, check_out_date)
        VALUES (?, ?, ?, ?, ?)
        ''', bookings_data)

        self.cursor.executemany('''
        INSERT INTO Payments (booking_id, amount, payment_date, payment_method)
        VALUES (?, ?, ?, ?)
        ''', payments_data)

        self.cursor.executemany('''
        INSERT INTO Staff (first_name, last_name, position, email, phone_number)
        VALUES (?, ?, ?, ?, ?)
        ''', staff_data)

        # cursor.executemany('''
        # INSERT INTO Services (name, description, price)
        # VALUES (?, ?, ?)
        # ''', services_data)




h = Hotel()