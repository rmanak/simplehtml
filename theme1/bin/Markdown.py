#!/usr/bin/env python3
import argparse
import html
import re
import sys
from typing import Iterable, List, Tuple


def _normalize_newlines(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.endswith("\n\n"):
        text += "\n\n"
    return text


def _split_blocks(text: str) -> List[str]:
    return [block for block in re.split(r"\n{2,}", text) if block.strip("\n")]


def _is_hr(block: str) -> bool:
    return re.match(r"\s*(\*\s*){3,}$", block) or re.match(r"\s*(-\s*){3,}$", block)


def _setext_heading(block: str) -> Tuple[int, str] | None:
    lines = block.split("\n")
    if len(lines) == 2:
        if re.match(r"^=+\s*$", lines[1]):
            return 1, lines[0]
        if re.match(r"^-+\s*$", lines[1]):
            return 2, lines[0]
    return None


def _atx_heading(block: str) -> Tuple[int, str] | None:
    match = re.match(r"^(#{1,6})\s*(.*?)\s*#*\s*$", block)
    if match:
        return len(match.group(1)), match.group(2)
    return None


def _is_code_block(block: str) -> bool:
    lines = block.split("\n")
    return all(line.startswith("    ") or line.startswith("\t") for line in lines if line)


def _strip_code_indent(lines: Iterable[str]) -> str:
    stripped = [line[4:] if line.startswith("    ") else line[1:] if line.startswith("\t") else line for line in lines]
    return "\n".join(stripped)


def _escape_code(text: str) -> str:
    return html.escape(text, quote=False)


def _inline_code(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        code = match.group(1)
        return f"<code>{html.escape(code, quote=False)}</code>"

    return re.sub(r"`([^`]+)`", replace, text)


def _inline_links(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        label, url = match.group(1), match.group(2)
        return f'<a href="{html.escape(url, quote=True)}">{label}</a>'

    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", replace, text)


def _inline_images(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        alt, url = match.group(1), match.group(2)
        return f'<img src="{html.escape(url, quote=True)}" alt="{html.escape(alt, quote=True)}" />'

    return re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", replace, text)


def _inline_emphasis(text: str) -> str:
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    text = re.sub(r"_([^_]+)_", r"<em>\1</em>", text)
    return text


def _apply_inline(text: str) -> str:
    text = _inline_code(text)
    text = _inline_images(text)
    text = _inline_links(text)
    text = _inline_emphasis(text)
    return text


def _render_paragraph(block: str) -> str:
    lines = block.split("\n")
    joined = "\n".join(lines)
    joined = _apply_inline(joined)
    joined = re.sub(r"\s+\n", "\n", joined)
    return f"<p>{joined}</p>"


def _render_list(lines: List[str], ordered: bool) -> str:
    tag = "ol" if ordered else "ul"
    items = []
    for line in lines:
        stripped = re.sub(r"^\s*(?:\d+\.|[\-*+])\s+", "", line)
        items.append(f"<li>{_apply_inline(stripped)}</li>")
    return f"<{tag}>\n" + "\n".join(items) + f"\n</{tag}>"


def _render_blockquote(block: str) -> str:
    lines = [re.sub(r"^>\s?", "", line) for line in block.split("\n")]
    inner = markdown("\n".join(lines))
    return f"<blockquote>\n{inner}\n</blockquote>"


def markdown(text: str) -> str:
    text = _normalize_newlines(text)
    blocks = _split_blocks(text)
    rendered: List[str] = []
    for block in blocks:
        if _is_hr(block):
            rendered.append("<hr />")
            continue

        setext = _setext_heading(block)
        if setext:
            level, title = setext
            rendered.append(f"<h{level}>{_apply_inline(title)}</h{level}>")
            continue

        atx = _atx_heading(block)
        if atx:
            level, title = atx
            rendered.append(f"<h{level}>{_apply_inline(title)}</h{level}>")
            continue

        if _is_code_block(block):
            code = _strip_code_indent(block.split("\n"))
            rendered.append(f"<pre><code>{_escape_code(code)}</code></pre>")
            continue

        if block.lstrip().startswith(">"):
            rendered.append(_render_blockquote(block))
            continue

        list_match = re.match(r"^\s*(\d+\.|[\-*+])\s+", block)
        if list_match:
            lines = [line for line in block.split("\n") if line.strip()]
            ordered = bool(re.match(r"^\s*\d+\.\s+", lines[0]))
            rendered.append(_render_list(lines, ordered))
            continue

        rendered.append(_render_paragraph(block))

    return "\n\n".join(rendered)


def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--shortversion", action="store_true")
    parser.add_argument("--html4tags", action="store_true")
    args, _unknown = parser.parse_known_args()

    version = "1.0.2b8"
    if args.version:
        sys.stdout.write(f"\nThis is Markdown, version {version}.\n")
        sys.stdout.write("Copyright 2004 John Gruber\n")
        sys.stdout.write("http://daringfireball.net/projects/markdown/\n\n")
        return
    if args.shortversion:
        sys.stdout.write(version)
        return

    text = sys.stdin.read()
    html_output = markdown(text)
    if args.html4tags:
        html_output = html_output.replace(" />", ">")
    sys.stdout.write(html_output)


if __name__ == "__main__":
    main()
