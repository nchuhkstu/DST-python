import math

BASE36_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def base63_encode(string):
    encoding = ""
    for char in string:

        char_code = ord(char)

        while char_code > 0:
            encoding += BASE36_CHARS[char_code % 36]
            char_code //= 36

        encoding = encoding[::-1]

    while len(encoding) < 11:
        encoding += "0"

    return encoding[:12]


def base63_decode(string):
    decoding = ""

    for i in range(0, len(string), 6):
        index = string[i:i + 6]

        char_code = 0
        power = 1

        while index != "":
            char_code += BASE36_CHARS.index(index[0]) * power
            power *= 63
            index = index[1:]

        decoding += chr(char_code)

    return decoding

print(base63_encode("KU_LFj7oMHe"))