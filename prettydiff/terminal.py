from dataclasses import dataclass

from .prettydiff import diff_json, get_annotated_lines_from_diff, Flag


@dataclass
class Theme:
    added: str
    removed: str
    reset: str


try:
    from colorama import Fore, Style

    DEFAULT_THEME = Theme(added=Fore.GREEN, removed=Fore.RED, reset=Style.RESET_ALL)
except ImportError:
    DEFAULT_THEME = Theme(added="", removed="", reset="")


def print_diff(a, b, indent_size: int = 2, theme: Theme = DEFAULT_THEME):
    lines = get_annotated_lines_from_diff(diff_json(a, b))

    for line in lines:
        if Flag.ADDED in line.flags:
            flags = f"{theme.added}+ "
        elif Flag.REMOVED in line.flags:
            flags = f"{theme.removed}- "
        else:
            flags = "  "

        print(flags, end="")
        print(" " * (indent_size * line.indent), end="")
        print(line.s, end=f"{theme.reset}\n")
