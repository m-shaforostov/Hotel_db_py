def convert_to_binary_file(file_name1, file_name2):
    with open(file_name1, "r", encoding='utf-8') as file1, open(file_name2, 'wb') as file2:
        file2.write(file1.read().encode('utf-8'))


def convert_from_binary_file(file_name1, file_name2):
    with open(file_name1, "rb") as file1, open(file_name2, 'w') as file2:
        file2.write(file1.read().decode('utf-8'))


convert_to_binary_file("guests_text_20", 'guests_text_20.dat')
convert_to_binary_file("rooms_text_20", 'rooms_text_20.dat')
convert_to_binary_file("bookings_text_20", 'bookings_text_20.dat')
convert_to_binary_file("payments_text_20", 'payments_text_20.dat')
convert_to_binary_file("staff_text_20", 'staff_text_20.dat')
