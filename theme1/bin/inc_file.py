#!/usr/bin/env python3
import re
import sys


def file_match(text: str) -> bool:
    return re.search(r'(<FILE=")(.*?)(">)', text, flags=re.DOTALL) is not None


def file_to_text(fname: str) -> str:
    try:
        with open(fname, "r") as input_file:
            return input_file.read()
    except OSError as exc:
        print(f"cannot open {fname}: {exc}", file=sys.stderr)
        return ""


def file_replace(text: str) -> str:
    match = re.match(r'(.*)(<FILE=")(.*?)(">)(.*)', text, flags=re.DOTALL)
    if not match:
        return text
    before, fname, after = match.group(1), match.group(3), match.group(5)
    file_content = file_to_text(fname)
    return f"{before}{file_content}{after}"


def main() -> None:
    content = sys.stdin.read()
    count = 0
    while file_match(content):
        content = file_replace(content)
        count += 1
        if count > 1000:
            raise RuntimeError("something went wrong!")
    sys.stdout.write(content)


if __name__ == "__main__":
    main()
