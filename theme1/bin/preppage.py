#!/usr/bin/env python3
import dataclasses
import os
import re
from datetime import datetime
import sys
from typing import Dict, Iterable, Tuple


@dataclasses.dataclass(frozen=True)
class Replacements:
    post_token: str = "JDHALOWPFHSNC"
    date_token: str = "ASDLKJFHG"
    sidebar_token: str = "KJDSADPFP"
    footer_token: str = "KDLPQHFZVD"
    download_token: str = "[dl]"
    external_token: str = "[>]"
    toc_token: str = "[TOC]"


META_FIELDS = ("title", "author", "keywords", "description")


def read_text(path: str) -> str:
    with open(path, "r") as handle:
        return handle.read()


def post_source_name(post_path: str) -> str:
    base_name = os.path.basename(post_path)
    if base_name.endswith(".w"):
        base_name = base_name[: -len(".w")]
    return f"{base_name}.txt"


def render_date(post_path: str) -> str:
    try:
        modified_time = os.path.getmtime(post_path)
        return datetime.fromtimestamp(modified_time).strftime("%a %b %d %Y")
    except OSError:
        return ""


def extract_metadata(post_text: str) -> Tuple[Dict[str, str], str]:
    metadata: Dict[str, str] = {}
    cleaned = post_text

    for field in META_FIELDS:
        pattern = rf"{field}\s*:=\s*{{\s*([^}}]*?)\s*}}"
        match = re.search(pattern, cleaned, flags=re.DOTALL)
        if match:
            metadata[field] = match.group(1)
            cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL)

    if "title" not in metadata:
        h1_match = re.search(r"(<h1>\s*)([^:]*)(:*)(\s*</h1>)", cleaned, flags=re.DOTALL)
        if h1_match:
            metadata["title"] = h1_match.group(2)

    return metadata, cleaned


def update_meta_tags(template: str, metadata: Dict[str, str]) -> str:
    if "title" in metadata:
        title_text = metadata["title"]
        template = re.sub(
            r"<title>.*</title>",
            lambda _match: f"<title>{title_text}</title>",
            template,
            flags=re.DOTALL,
        )

    meta_patterns = {
        "keywords": r'(<meta name="keywords" content=")([^"]*)(" />)',
        "author": r'(<meta name="author" content=")([^"]*)(" />)',
        "description": r'(<meta name="description" content=")([^"]*)(" />)',
    }

    for key, pattern in meta_patterns.items():
        if key in metadata:
            value = metadata[key]
            template = re.sub(
                pattern,
                lambda match, value=value: f"{match.group(1)}{value}{match.group(3)}",
                template,
                flags=re.DOTALL,
            )

    return template


def build_reference_block(post_text: str) -> str:
    ref_numbers: Dict[str, int] = {}
    next_ref = 0
    ref_html = []

    def replace_reference(match: re.Match[str]) -> str:
        nonlocal next_ref
        label = match.group(2)
        if label not in ref_numbers:
            next_ref += 1
            ref_numbers[label] = next_ref
            definition = re.search(rf"(\{{\s*{re.escape(label)}\s*:\s*)([^}}]*)(\}})", post_text, flags=re.DOTALL)
            if definition:
                entry = (
                    f'<a href="#cnt{label}" id="ref{label}">[{next_ref}]</a>: '
                    f"{definition.group(2)}"
                )
                ref_html.append(f"<p>{entry}</p>")
        ref_id = ref_numbers[label]
        return f'<sup><a href="#ref{label}" id="cnt{label}">[{ref_id}]</a></sup>'

    ref_pattern = re.compile(r"(%%\s*)(\w+.*?)(\s*%%)")
    while ref_pattern.search(post_text):
        post_text = ref_pattern.sub(replace_reference, post_text, count=1)
        for label in list(ref_numbers):
            post_text = re.sub(
                rf"(\{{\s*{re.escape(label)}\s*:\s*)([^}}]*)(\}})",
                "",
                post_text,
                flags=re.DOTALL,
            )

    if ref_html:
        return f"{post_text}<hr /><h2>References</h2>{''.join(ref_html)}"

    return post_text


def apply_shortcodes(text: str, tokens: Replacements) -> str:
    replacements = {
        tokens.external_token: (
            '<img style="margin-left:1px;" src="img/external-link.svg" alt="" align="bottom" />'
        ),
        tokens.download_token: '<img src="img/dl.svg" />',
        tokens.toc_token: '<div class="table_of_contents"></div>',
    }
    for source, target in replacements.items():
        text = re.sub(re.escape(source), target, text)
    return text


def apply_image_macros(text: str) -> str:
    right_box = (
        '<div style="max-width:350px; width:auto; padding:2px; height:auto; text-align:justify; '
        'border: solid #BBBBBB 1px;float:right; margin-left:8px;">'
        '<img style="display:block; height:auto; width:auto; max-width:320px; '
        'margin-left:auto; margin-right:auto;" src="'
    )
    right_alt = '" alt="'
    right_caption = '" border="0" /><hr />'
    right_no_caption = '" border="0" />'
    right_close = "</div>"

    text = re.sub(
        r"({{}}\(\()(.*?)(\)\))",
        rf"{right_box}\2{right_alt}{right_no_caption}{right_close}",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"({{)(.*?)(}}\(\()(.*?)(\)\))",
        rf"{right_box}\4{right_alt}{right_caption}\2{right_close}",
        text,
        flags=re.DOTALL,
    )

    center_box = (
        '<div style="margin-left:auto; margin-right:auto; padding:3px; text-align:justify; '
        'border:solid #BBBBBB 1px; height:auto; width: auto; max-width:500px;">'
        '<img style="display:block; height:auto; width:auto; max-width:470px; '
        'margin-left:auto; margin-right:auto;" src="'
    )
    center_alt = '" alt="'
    center_caption = '" border="0" /><hr />'
    center_no_caption = '" border="0" />'
    center_close = "</div>"

    text = re.sub(
        r"({{}}\[\[)(.*?)(\]\])",
        rf"{center_box}\2{center_alt}{center_no_caption}{center_close}",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"({{)(.*?)(}}\[\[)(.*?)(\]\])",
        rf"{center_box}\4{center_alt}{center_caption}\2{center_close}",
        text,
        flags=re.DOTALL,
    )

    right_wrap = (
        '<div style="max-width:350px; width:auto; padding:2px; height:auto; text-align:justify; '
        'border: solid #BBBBBB 1px;float:right; margin-left:8px;">'
    )
    text = re.sub(r"(<R>)(.*?)(</R>)", rf"{right_wrap}\2</div>", text, flags=re.DOTALL)

    return text


def replace_placeholders(
    template: str,
    post_text: str,
    sidebar_text: str,
    footer_text: str,
    date_text: str,
    tokens: Replacements,
) -> str:
    replacements = {
        tokens.date_token: date_text,
        tokens.post_token: post_text,
        tokens.sidebar_token: sidebar_text,
        tokens.footer_token: footer_text,
    }
    for source, target in replacements.items():
        template = template.replace(source, target)
    return template


def main() -> None:
    if len(sys.argv) != 5:
        raise SystemExit("\n  Usage: xxx file\n\n")

    tokens = Replacements()
    template_file, side_file, foot_file, post_file = sys.argv[1:5]

    post_source = post_source_name(post_file)
    template = read_text(template_file)
    post_text = read_text(post_file)
    sidebar_text = read_text(side_file)
    footer_text = read_text(foot_file)

    metadata, post_text = extract_metadata(post_text)
    post_text = build_reference_block(post_text)

    date_text = render_date(post_source)
    template = update_meta_tags(template, metadata)

    output = replace_placeholders(
        template,
        post_text,
        sidebar_text,
        footer_text,
        date_text,
        tokens,
    )
    output = apply_shortcodes(output, tokens)
    output = apply_image_macros(output)

    sys.stdout.write(output)


if __name__ == "__main__":
    main()
