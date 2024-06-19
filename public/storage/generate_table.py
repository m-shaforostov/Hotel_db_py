import random
from datetime import datetime, timedelta


def generate_guests_data(num_rows):
    first_names = [
        "Emma", "Liam", "Olivia", "Noah", "Ava",
        "Mason", "Sophia", "Ethan", "Isabella", "Lucas",
        "Mia", "Alexander", "Amelia", "Benjamin", "Harper",
        "Elijah", "Evelyn", "James", "Abigail", "Logan"
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones",
        "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
        "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin"
    ]


    guests_data = []
    for _ in range(num_rows):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        number = str(random.randint(950000000, 959999999))
        phone_number = f"+421-{number[:2]}-{number[2:5]}-{number[5:]}"
        age = random.randint(18, 70)

        row = f"{first_name};{last_name};{email};{phone_number}\n"
        guests_data.append(row)

    return ''.join(guests_data)


def generate_rooms_data(num_rooms):
    rooms_data = []
    for room_number in range(101, 101 + num_rooms):
        if room_number % 10 == 0:
            beds_type = 4
        else:
            beds_type = random.randint(1, 3)

        price_per_night = 50 + 10 * beds_type
        availability_status = random.choice(['Available', 'Occupied', 'Reserved'])
        bathroom_type = random.choice(['Shower', 'Bath'])
        balcony = random.choice([True, False])
        side_of_building = random.choice(['North', 'South'])

        row = f"{room_number};{beds_type};{price_per_night};{availability_status};{bathroom_type};{balcony};{side_of_building}\n"
        rooms_data.append(row)

    return ''.join(rooms_data)


def generate_bookings_data(num_rows, num_guests, num_rooms):
    bookings_data = []
    base_date = datetime(2024, 6, 1)

    for _ in range(num_rows):
        guest_id = random.randint(1, num_guests)
        room_id = random.randint(101, 100 + num_rooms)
        check_in_date = base_date + timedelta(days=random.randint(0, 30))
        nights_stayed = random.randint(1, 10)
        check_out_date = check_in_date + timedelta(days=nights_stayed)

        row = f"{guest_id};{room_id};{check_in_date.strftime('%Y-%m-%d')};{nights_stayed};{check_out_date.strftime('%Y-%m-%d')}\n"
        bookings_data.append(row)

    return ''.join(bookings_data)


def parse_data(data_text):
    return [line.split(';') for line in data_text.strip().split('\n')]

def generate_payments_data(bookings_data, room_prices):
    payments_data = []
    payment_methods = ['Credit Card', 'Cash']

    for booking_id, booking in enumerate(bookings_data, 1):
        room_id = int(booking[1]) % 100
        nights_stayed = int(booking[3])
        price_per_night = room_prices[room_id]
        amount = nights_stayed * price_per_night
        payment_method = random.choice(payment_methods)
        check_in_date = datetime.strptime(booking[2], '%Y-%m-%d')
        payment_date = (check_in_date - timedelta(days=random.randint(1, 3))).strftime('%Y-%m-%d')

        row = f"{booking_id};{amount};{payment_date};{payment_method}\n"
        payments_data.append(row)

    return ''.join(payments_data)


def generate_staff_data(num_rows):
    first_names = ['John', 'Jane', 'Alice', 'Michael', 'Laura']
    last_names = ['Doe', 'Smith', 'Johnson', 'Brown', 'Davis']
    positions = ['Manager', 'Receptionist', 'Cleaner', 'Security']

    staff_data = []
    for _ in range(num_rows):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        position = random.choice(positions)
        email = f"{first_name.lower()}.{last_name.lower()}@hotel.com"
        number = random.randint(950000000, 959999999)
        phone_number = f"+421-{number // 10000000}-{number % 10000000 // 10000}-{number % 10000}"

        row = f"{first_name};{last_name};{position};{email};{phone_number}\n"
        staff_data.append(row)

    return ''.join(staff_data)

def convert_to_binary_file(data_text, file_name):
    with open(file_name, 'wb') as file:
        file.write(data_text.encode('utf-8'))

def write_into_file(file_name, data):
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(data)


a = 50
guests_data_text = generate_guests_data(a)
print(guests_data_text)
write_into_file("../backup/guests_data_text", guests_data_text)
#
rooms_data_text = generate_rooms_data(a)
print(rooms_data_text)
write_into_file("../backup/rooms_data_text", rooms_data_text)

bookings_data_text = generate_bookings_data(a-10, a-10, a)
print(bookings_data_text)
write_into_file("../backup/bookings_data_text", bookings_data_text)

bookings_data = parse_data(bookings_data_text)
rooms_data = parse_data(rooms_data_text)

room_prices = {int(room[0]) % 100: float(room[2][:-1]) for room in rooms_data}

payments_data_text = generate_payments_data(bookings_data, room_prices)
print(payments_data_text)
write_into_file("../backup/payments_data_text", payments_data_text)

# staff_data_text = generate_staff_data(100)
# print(staff_data_text)
# write_into_file("../backup/staff_data_text", staff_data_text)

