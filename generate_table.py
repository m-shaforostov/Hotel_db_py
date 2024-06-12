import random

# Generate sample data for the Rooms table
def generate_rooms_data(num_rooms):
    rooms_data = []
    for room_number in range(121, 121 + num_rooms):
        if room_number % 10 == 0:
            room_type = 'Quadruple'
            num_beds = 4
        else:
            room_type = random.choice(['Single', 'Double', 'Triple'])
            num_beds = room_type.count('e') + 1  # Count 'e' in Single, Double, Triple

        price_per_night = 50 + 10 * num_beds
        availability_status = random.choice(['Available', 'Occupied', 'Reserved'])
        bathroom_type = random.choice(['Shower', 'Bath', 'None'])
        balcony = random.choice([True, False])
        if (room_number // 10) % 2 == 0:
            side_of_building = 'North'
        else:
            side_of_building = 'South'
        row = f"{room_number};{room_type};{price_per_night:.2f};{availability_status};{bathroom_type};{balcony};{side_of_building}\n"
        rooms_data.append(row)

    return ''.join(rooms_data)

# Generate 20 rows of data for the Rooms table
rooms_data_text = generate_rooms_data(80)

# Print the generated data
print(rooms_data_text)
