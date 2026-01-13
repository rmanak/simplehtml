#!/usr/bin/env python3
import sys

import markdown


def main() -> None:
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as handle:
            text = handle.read()
    else:
        text = sys.stdin.read()

    html = markdown.markdown(
        text,
        extensions=[
            "pymdownx.arithmatex",
        ],
        extension_configs={
            "pymdownx.arithmatex": {
                "generic": True
            }
        }
    )
    sys.stdout.write(html)


if __name__ == "__main__":
    main()
