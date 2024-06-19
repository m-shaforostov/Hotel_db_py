def convert_to_binary_file(file_name1, file_name2):
    with open(file_name1, "r", encoding='utf-8') as file1, open(file_name2, 'wb') as file2:
        file1_data = file1.read().split("\n")
        for row in file1_data:
            row = row.split(";")
            for element in row:
                file2.write(element.encode('utf-8') + b'\x00')
            file2.write(b'\x00')


def parse_to_array(file_name):
    with open(file_name, "rb") as file:
        data = file.read()
        data_array = []
        row_array = []
        for row in data.split(b'\x00\x00')[:-1]:
            for element in row.split(b'\x00'):
                element = element.decode()
                if element.isdigit():
                    element = int(element)
                row_array.append(element)
            data_array.append(tuple(row_array))
        return data_array

def convert_from_array(array, file_name):
    with open(file_name, 'w') as file:
        for row in array:
            file.write(";".join(row) + "\n")


convert_to_binary_file("../backup/guests_data_text", 'guests_data_text.dat')
convert_to_binary_file("../backup/bookings_data_text", 'bookings_data_text.dat')
convert_to_binary_file("../backup/payments_data_text", 'payments_data_text.dat')
convert_to_binary_file("../backup/rooms_data_text", 'rooms_data_text.dat')
# convert_to_binary_file("../backup/staff_data_text", 'staff_data_text.dat')
