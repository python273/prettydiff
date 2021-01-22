# prettydiff

**prettydiff** - diff parsed JSON objects and pretty-print it

> `$ python3 -m pip install prettydiff`

- [Custom output format example (HTML)](https://github.com/python273/prettydiff/blob/master/example_html.py)

## terminal

```python
from prettydiff import print_diff

a = {"a": "hello", "b": True, "c": [1, 3], "d": {"e": {"f": 1}}}
b = {"a": "world", "b": False, "c": [1, 2, 3]}

# to enable colors: $ python3 -m pip install prettydiff[terminal]
print_diff(a, b)
```

```diff
  {
-   'a': 'hello',
+   'a': 'world',
-   'b': True,
+   'b': False,
    'c': [
      1,
-     3,
+     2,
+     3,
    ],
-   'd': {
-     'e': {
-       'f': 1,
-     },
-   },
  }
```
