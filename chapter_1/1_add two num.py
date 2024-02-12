def convert_integer(number_string):
    converted_integer = int(number_string)
    return converted_integer


def Sum(num_1, num_2):
    num_1_int = convert_integer(num_1)
    num_2_int = convert_integer(num_2)

    result = num_1_int + num_2_int
    return result


print(Sum("1", "2"))
