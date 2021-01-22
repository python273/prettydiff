from prettydiff import print_diff

a = {"a": "hello", "b": True, "c": [1, 3], "d": {"e": {"f": 1}}}
b = {"a": "world", "b": False, "c": [1, 2, 3]}

# to enable colors: $ python3 -m pip install prettydiff[terminal]
print_diff(a, b)
