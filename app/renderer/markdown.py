import re
from markdown_it import MarkdownIt


_md = MarkdownIt("commonmark", {'html': False, 'linkify': True, 'typographer': True})


SIGNIFIER_MAP: dict[str, str] = {
    "*": "priority",
    "x": "done",
    ">": "migrated",
    "<": "scheduled",
    "o": "event",
    "-": "note",
    "!": "inspiration",
}


def _preprocess_signifiers(text: str) -> str:
    def replace_line(match: re.Match[str]) -> str:
        symbol = match.group(1)
        rest = match.group(2)
        token = SIGNIFIER_MAP.get(symbol, "unknown")
        return f"- @sig({token}) {rest}"

    pattern = re.compile(r"^(\*|x|>|<|o|-|!)[\t ]+(.*)$", re.MULTILINE)
    return pattern.sub(replace_line, text)


def _decorate_signifiers(html: str) -> str:
    # Replace '@sig(token)' at start of list items by a span icon
    def repl(match: re.Match[str]) -> str:
        token = match.group(1)
        icon = {
            "priority": "★",
            "done": "✔",
            "migrated": "»",
            "scheduled": "«",
            "event": "○",
            "note": "–",
            "inspiration": "!",
        }.get(token, "•")
        return f"<li class=\"bj-li\"><span class=\"bj-sign bj-{token}\">{icon}</span> "

    return re.sub(r"<li>@sig\(([^)]+)\)\s*", repl, html)


def render_markdown_with_signifiers(text: str) -> str:
    pre = _preprocess_signifiers(text)
    html = _md.render(pre)
    html = _decorate_signifiers(html)
    styles = """
    <style>
      body { font-family: Segoe UI, Arial, sans-serif; padding: 12px; }
      ul, ol { list-style-position: outside; padding-left: 1.6em; margin-left: 0; }
      li.bj-li { list-style-type: none; position: relative; padding-left: 1.6em; }
      li.bj-li::marker { content: ''; }
      .bj-sign { position: absolute; left: 0; width: 1.2em; text-align: center; margin-right: 6px; color: #444; }
      .bj-priority { color: #d97706; }
      .bj-done { color: #16a34a; }
      .bj-migrated { color: #2563eb; }
      .bj-scheduled { color: #0ea5e9; }
      .bj-event { color: #6b7280; }
      .bj-note { color: #6b7280; }
      .bj-inspiration { color: #db2777; font-weight: 700; }
      pre, code { background: #f3f4f6; }
    </style>
    """
    return styles + html


