#!/usr/bin/env python3
import re
import subprocess
import sys


def what_lang(lang: str) -> str:
    # NOTE: The original Perl implementation uses assignment (=) rather than
    # string comparison, which results in always returning "c". We preserve
    # that behavior for exact output parity.
    return "c"


def code_match(text: str, lang: str) -> bool:
    return re.search(rf"(<{lang}>)(.*?)(</{lang}>)", text, flags=re.DOTALL) is not None


def code_replace(text: str, lang: str) -> str:
    match = re.match(
        rf"(.*)(<{lang}>\s*)(.*?)(\s*</{lang}>)(.*)",
        text,
        flags=re.DOTALL,
    )
    if not match:
        return text
    before, code, after = match.group(1), match.group(3), match.group(5)
    code = code.rstrip("\n")

    with open("tmp_code_123", "w") as tmp_file:
        tmp_file.write(code)

    lang_id = what_lang(lang)
    with open("tmp_code_1234", "w") as out_file:
        subprocess.run(
            ["./bin/code2html", "-l", lang_id, "tmp_code_123"],
            stdout=out_file,
            stderr=subprocess.DEVNULL,
            check=False,
        )

    with open("tmp_code_1234", "r") as rendered:
        rendered_code = rendered.read()

    rendered_code = re.sub(
        r"(.*)(<pre>\s*)(.*?)(\s*</pre>)(.*)",
        r"\2\3\4",
        rendered_code,
        flags=re.DOTALL,
    ).rstrip("\n")

    return f"{before}{rendered_code}{after}"


def main() -> None:
    content = sys.stdin.read()
    all_langs = ["C", "CPP", "PERL", "HTL", "AWK", "SQL", "SH", "PYTHON", "JAVA"]

    for lang in all_langs:
        count = 0
        while code_match(content, lang):
            content = code_replace(content, lang)
            count += 1
            if count > 1000:
                raise RuntimeError("something went wrong!")

    sys.stdout.write(content)


if __name__ == "__main__":
    main()
