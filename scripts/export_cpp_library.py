"""Export selected lesson library blocks as code to paste into user.cpp."""
from __future__ import annotations

import argparse
from pathlib import Path

from cpp_library import assemble_library, read_library_snippets


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--list", action="store_true", help="list available block names")
    mode.add_argument("--blocks", nargs="+", help="block names in the desired order")
    parser.add_argument("--output", type=Path, help="destination C++ source fragment")
    args = parser.parse_args()
    if args.list:
        if args.output:
            parser.error("--output requires --blocks")
        print("\n".join(read_library_snippets()))
        return
    if not args.output:
        parser.error("--blocks requires --output")
    try:
        source = assemble_library(args.blocks)
    except ValueError as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(source)
    print(f"Wrote {len(dict.fromkeys(args.blocks))} header-free blocks to {args.output}")


if __name__ == "__main__":
    main()
