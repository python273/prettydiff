import html

from prettydiff import diff_json, get_annotated_lines_from_diff, Flag


HTML_START = """
<!doctype html>
<html lang=en>
<head>
    <meta charset=utf-8>
    <title>Pretty HTML diff</title>
    <style>
        .text-monospace {font-family: monospace;}
        .text-added {color: green;}
        .text-removed {color: red;}
    </style>
</head>
<body>
"""

HTML_END = """
</body>
</html>
"""


def diff_html_iter(a, b, indent_size=2):
    lines = get_annotated_lines_from_diff(diff_json(a, b))

    yield HTML_START
    yield '<div class="text-monospace">\n'

    for line in lines:
        if Flag.ADDED in line.flags:
            yield f'<span id="change_{line.change_id}" class="text-added">+&nbsp;'
        elif Flag.REMOVED in line.flags:
            yield f'<span id="change_{line.change_id}" class="text-removed">-&nbsp;'
        else:
            yield "<span>&nbsp;&nbsp;"

        yield "&nbsp;" * (indent_size * line.indent)
        yield html.escape(line.s)
        yield "</span></br>\n"

    yield "</div>"
    yield HTML_END


def diff_html(a, b, indent_size=2):
    return "".join(diff_html_iter(a, b, indent_size=indent_size))


if __name__ == "__main__":
    a = {"a": "hello", "b": [1], "c": {"d": {"f": 1}}}
    b = {"a": "world", "b": [1, 2]}

    out = diff_html(a, b)

    with open("html_diff_out.html", "w") as f:
        f.write(out)
