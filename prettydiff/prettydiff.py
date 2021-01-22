"""
- [ ] TODO folding objects?
- [ ] TODO skipping unchanged in lists?
"""

from enum import Enum, auto
import itertools

from .diff_obj import diff_json, Diff, UNDEFINED

try:
    from colorama import Fore, Style

    class Colors:
        BLUE = Fore.BLUE
        RED = Fore.RED
        RESET = Style.RESET_ALL


except ImportError:

    class Colors:
        BLUE = ""
        RED = ""
        RESET = ""


INDENT = " " * 4


class ChangeId:
    def __init__(self, _id):
        self.id = _id

    def __repr__(self):
        return f"<ChangeId {self.id}>"

    def __str__(self):
        return str(self.id)


class Flag(Enum):
    ADDED = auto()
    REMOVED = auto()


class AnnotatedLine:
    def __init__(self, s, indent, flags=None, change_id=None):
        self.s = s
        self.indent = indent
        self.flags = flags if flags else []
        self.change_id = change_id

    def __repr__(self):
        return f"<AnnotatedLine {self.indent} {repr(self.s)} {self.flags} {self.change_id}>"


class Part:
    def __init__(
        self, children, indent=0, prefix="", postfix="", flags=None, change_id=None
    ):
        self.children = children if isinstance(children, list) else [children]
        self.indent = indent
        self.prefix = prefix
        self.postfix = postfix
        self.flags = flags if flags else []
        self.change_id = change_id

    def __repr__(self):
        out = []

        out.append(Colors.RESET)
        out.append("<Part")

        out.append(f" {self.indent}")
        out.append(f" {self.flags}")
        out.append(f" {self.change_id}")

        if self.prefix:
            out.append(Colors.RED)
            out.append(f" {repr(self.prefix)}")
            out.append(Colors.RESET)

        if isinstance(self.children, list):
            out.append(" [\n")
            s = ",\n".join(
                "\n".join(INDENT + i for i in str(i).split("\n")) for i in self.children
            )
            out.append(s)
            out.append("\n] ")
        else:
            out.append(self.children)

        if self.postfix:
            out.append(Colors.BLUE)
            out.append(f" {repr(self.postfix)}")
            out.append(Colors.RESET)

        out.append(">")

        return "".join(str(i) for i in out)


def _set_flags_deep(p: Part, flags: list):
    for i in p.children:
        if isinstance(i, Part):
            i.flags = flags
            _set_flags_deep(i, flags)


def _set_change_id_deep(p: Part, change_id: ChangeId):
    for i in p.children:
        if isinstance(i, Part):
            i.change_id = change_id
            _set_change_id_deep(i, change_id)


def _add_dict_item(append, k, v, id_gen, flags=None, change_id=None):
    if v is not UNDEFINED:
        p = Part(
            _diff_to_parts(v, id_gen=id_gen),
            indent=0,
            prefix=f"{repr(k)}: ",
            postfix=",\n",
            flags=flags,
            change_id=change_id,
        )
        if flags:
            _set_flags_deep(p, flags)
        if change_id:
            _set_change_id_deep(p, change_id)

        append(p)


def _add_list_item(append, v, id_gen, flags=None, change_id=None):
    # TODO: option to not add last comma

    if v is not UNDEFINED:
        p = Part(
            _diff_to_parts(v, id_gen=id_gen),
            indent=0,
            postfix=",\n",
            flags=flags,
            change_id=change_id,
        )
        if flags:
            _set_flags_deep(p, flags)
        if change_id:
            _set_change_id_deep(p, change_id)

        append(p)


def _diff_to_parts(diff, id_gen=None):
    if id_gen is None:
        id_gen = itertools.count()

    if isinstance(diff, dict):
        out = []

        for k, v in diff.items():
            if isinstance(v, Diff):
                change_id = ChangeId(next(id_gen))
                _add_dict_item(
                    out.append, k, v.removed, id_gen, [Flag.REMOVED], change_id
                )
                _add_dict_item(out.append, k, v.added, id_gen, [Flag.ADDED], change_id)
            else:
                _add_dict_item(out.append, k, v, id_gen)

        return Part(out, indent=1, prefix="{\n", postfix="}")
    elif isinstance(diff, list):
        out = []

        for x, v in enumerate(diff):
            if isinstance(v, Diff):
                change_id = ChangeId(next(id_gen))
                _add_list_item(out.append, v.removed, id_gen, [Flag.REMOVED], change_id)
                _add_list_item(out.append, v.added, id_gen, [Flag.ADDED], change_id)
            else:
                _add_list_item(out.append, v, id_gen)

        return Part(out, indent=1, prefix="[\n", postfix="]")
    else:
        return Part(repr(diff))

    raise Exception


def _get_annotated_dirty(r, _indent=0):
    if not isinstance(r, list):
        r = [r]

    out = []

    for i in r:
        if isinstance(i, Part):
            if i.prefix:
                out.append(
                    AnnotatedLine(
                        i.prefix, indent=_indent, flags=i.flags, change_id=i.change_id
                    )
                )

            nested_out = _get_annotated_dirty(i.children, _indent=_indent + i.indent)

            if i.flags:
                for nested_line in nested_out:
                    nested_line.flags = i.flags

            if i.change_id:
                for nested_line in nested_out:
                    nested_line.change_id = i.change_id

            out.extend(nested_out)

            if i.postfix:
                out.append(
                    AnnotatedLine(
                        i.postfix, indent=_indent, flags=i.flags, change_id=i.change_id
                    )
                )
        else:
            out.append(AnnotatedLine(i, indent=_indent))

    return out


def _clean_annotated_lines(r):
    out = []

    add_to = None
    for i in r:
        if add_to is not None:
            add_to.s += i.s
            if i.s.endswith("\n"):
                out.append(add_to)
                add_to = None
        elif not i.s.endswith("\n") and add_to is None:
            add_to = i
        else:
            out.append(i)

    if add_to is not None:
        out.append(add_to)

    for i in out:
        i.s = i.s.rstrip("\n")

    return out


def get_annotated_lines_from_diff(diff):
    return _clean_annotated_lines(_get_annotated_dirty(_diff_to_parts(diff)))
