import re

ALLOWED_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode(input_str):

  # Remove disallowed chars
  cleaned_str = re.sub(r"[^a-zA-Z0-9_]", "", input_str)

  # Convert to uppercase
  cleaned_str = cleaned_str.upper()

  # Remove underscores
  cleaned_str = cleaned_str.replace("_", "")

  return cleaned_str

def test():
  inputs = [
    "KU_3PjzsHmK",
    "hello456_test78",
    "numB3r5_andL3tt3rs"
  ]

  for input in inputs:
    output = encode(input)
    print(f"{input} -> {output}")

test()

A7G264USVLD8

KU_0Z4zpzMe

ALLOWED_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

A 11
7 8
K 21
U 31

A7H0T9AKA434
KU_8EfLHH1a

A7HFUMEL99V7
KU_B_MTLAVd


"A7IKVD3SIP38" "KU_LFj7oMHe"

"A7IKVD3SJ3P2" "KU_LFj7oOyY"

"A7IKVD3SK255" "KU_LFj7oWYb"

7LITXkklwbj9Wzh
7LITXkklwbjBhFy