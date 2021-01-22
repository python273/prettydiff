"""
- [ ] TODO change spec format?
- [ ] TODO SPEC: allow to ignore fields
"""

import itertools
import unittest
from unittest import TestCase


class UNDEFINED_Class:
    def __repr__(self):
        return "UNDEFINED"

    def __str__(self):
        return self.__repr__()


UNDEFINED = UNDEFINED_Class()


class Diff:
    def __init__(self, removed, added):
        self.removed = removed
        self.added = added

    def __repr__(self):
        out = ["<Diff"]

        if self.removed is not UNDEFINED:
            out.append(f"removed={repr(self.removed)}")

        if self.added is not UNDEFINED:
            out.append(f"added={repr(self.added)}")

        out.append(">")

        return " ".join(out)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.removed == other.removed and self.added == other.added


def omit(d, keys):
    return {k: v for k, v in d.items() if k not in keys}


def diff_json(old, new, spec=None, _path=None):
    if _path is None:
        _path = ""

    if isinstance(old, dict) and isinstance(new, dict):
        diff = {}

        checked_keys = set()

        for k in itertools.chain(old.keys(), new.keys()):  # to persist order
            if k in checked_keys:
                continue
            checked_keys.add(k)

            old_value = old.get(k, UNDEFINED)
            new_value = new.get(k, UNDEFINED)

            p = f'{_path}["{k}"]'
            diff[k] = diff_json(old_value, new_value, spec=spec, _path=p)  # TODO spec

        return diff
    elif isinstance(old, list) and isinstance(new, list):
        d = spec.get(_path) if spec else None

        if d and d["type"] == "unique-value-match":
            sk = d["key"]

            old_by_key = {i[sk]: i for i in old}
            new_by_key = {i[sk]: i for i in new}

            keys = set(old_by_key.keys()) | set(new_by_key.keys())
            diff = []

            for k in keys:
                old_value = old_by_key.get(k, UNDEFINED)
                new_value = new_by_key.get(k, UNDEFINED)
                p = f'{_path}["{sk}" == {repr(k)}]'
                r = diff_json(old_value, new_value, spec=spec, _path=p)
                diff.append(r)

            return diff
        else:
            diff = []

            for i in range(max(len(old), len(new))):
                try:
                    old_value = old[i]
                except IndexError:
                    old_value = UNDEFINED

                try:
                    new_value = new[i]
                except IndexError:
                    new_value = UNDEFINED

                diff.append(diff_json(old_value, new_value, spec=spec))

            return diff

    elif old is UNDEFINED or new is UNDEFINED or type(old) != type(new) or old != new:
        return Diff(old, new)

    assert type(old) == type(new)
    assert old == new

    return old


class DiffJsonTestCase(TestCase):
    def test_dict_simple(self):
        a = {"a": 1}

        b = {"a": 2}

        r = diff_json(a, b)
        self.assertEqual(r, {"a": Diff(1, 2)})

    def test_dict_new_key(self):
        a = {
            "a": 1,
        }

        b = {
            "a": 1,
            "b": 1,
        }

        r = diff_json(a, b)
        self.assertEqual(r, {"a": 1, "b": Diff(UNDEFINED, 1)})

    def test_dict_removed_key(self):
        a = {
            "a": 1,
            "b": 1,
        }

        b = {
            "a": 1,
        }

        r = diff_json(a, b)
        self.assertEqual(r, {"a": 1, "b": Diff(1, UNDEFINED)})

    def test_dict_nested(self):
        a = {
            "a": {"x": 1},
        }

        b = {
            "a": {"x": 2},
        }

        r = diff_json(a, b)
        self.assertEqual(r, {"a": {"x": Diff(1, 2)}})

    def test_dict_nested_list(self):
        a = {"a": [{"id": 1, "value": 1}]}

        b = {"a": [{"id": 1, "value": 2}]}

        r = diff_json(a, b, spec={'["a"]': {"type": "unique-value-match", "key": "id"}})
        self.assertEqual(r, {"a": [{"id": 1, "value": Diff(1, 2)}]})

    def test_list_by_id(self):
        a = [{"id": 1, "value": 1}]
        b = [{"id": 1, "value": 2}]

        r = diff_json(a, b, spec={"": {"type": "unique-value-match", "key": "id"}})
        self.assertEqual(r, [{"id": 1, "value": Diff(1, 2)}])

    def test_list_by_id_added(self):
        a = [{"id": 1, "value": 1}]
        b = [{"id": 1, "value": 1}, {"id": 2, "value": 2}]

        r = diff_json(a, b, spec={"": {"type": "unique-value-match", "key": "id"}})
        self.assertEqual(
            r, [{"id": 1, "value": 1}, Diff(UNDEFINED, {"id": 2, "value": 2})]
        )

    def test_list_by_id_removed(self):
        a = [{"id": 1, "value": 1}, {"id": 2, "value": 2}]
        b = [{"id": 1, "value": 1}]

        r = diff_json(a, b, spec={"": {"type": "unique-value-match", "key": "id"}})
        self.assertEqual(
            r, [{"id": 1, "value": 1}, Diff({"id": 2, "value": 2}, UNDEFINED)]
        )

    def test_list_by_id_removed_in_middle(self):
        a = [{"id": 1, "value": 1}, {"id": 2, "value": 2}, {"id": 3, "value": 3}]
        b = [{"id": 1, "value": 1}, {"id": 3, "value": 3}]

        r = diff_json(a, b, spec={"": {"type": "unique-value-match", "key": "id"}})
        self.assertEqual(
            r,
            [
                {"id": 1, "value": 1},
                Diff({"id": 2, "value": 2}, UNDEFINED),
                {"id": 3, "value": 3},
            ],
        )

    def test_dict_list_new_item(self):
        a = [1, 2]
        b = [1, 2, 3]

        r = diff_json(a, b)
        self.assertEqual(r, [1, 2, Diff(UNDEFINED, 3)])

    def test_dict_list_removed_item(self):
        a = [1, 2, 3]
        b = [1, 2]

        r = diff_json(a, b)
        self.assertEqual(r, [1, 2, Diff(3, UNDEFINED)])


if __name__ == "__main__":
    unittest.main()
