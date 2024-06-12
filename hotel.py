import sqlite3


class Hotel:
    def __init__(self):
        connection = sqlite3.connect('hotel.db')  # Connect to/create
        cursor = connection.cursor()

        # Create some tables -------------------------------------------------------------------------------------------
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Guests (
                guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                gender TEXT,
                age INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Rooms (
                room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number TEXT NOT NULL,
                type TEXT NOT NULL,
                price_per_night REAL NOT NULL,
                availability_status TEXT NOT NULL,
                bathroom_type TEXT,
                balcony BOOLEAN,
                side_of_building TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_id INTEGER,
                room_id INTEGER,
                check_in_date TEXT NOT NULL,
                check_out_date TEXT NOT NULL,
                FOREIGN KEY (guest_id) REFERENCES Guests (guest_id),
                FOREIGN KEY (room_id) REFERENCES Rooms (room_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER,
                amount REAL NOT NULL,
                payment_date TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                FOREIGN KEY (booking_id) REFERENCES Bookings (booking_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Staff (
                staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                position TEXT NOT NULL,
                email TEXT NOT NULL,
                phone_number TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Services (
                service_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL
            )
        ''')

        # --------------------------------------------------------------------------------------------------------------

        connection.commit()
        connection.close()


h = Hotel()