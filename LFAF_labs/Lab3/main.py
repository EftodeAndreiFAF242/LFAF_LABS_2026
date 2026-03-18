"""
main.py  —  ArcaneScript Lexer entry point
-------------------------------------------
Run:
    python main.py                    # tokenise the built-in sample
    python main.py path/to/file.arc   # tokenise a custom .arc file
"""

import sys
import os
from lexer import Lexer, LexerError
from arc_token import TokenType


# ---------------------------------------------------------------------------
# Pretty-printing helpers
# ---------------------------------------------------------------------------

# Token types that are "noise" for a summary view (skip newlines in table)
_SKIP_IN_SUMMARY = {TokenType.NEWLINE}

COL_W = {
    "type":  22,
    "value": 25,
    "line":   6,
    "col":    6,
}

DIVIDER = (
    "+" + "-" * (COL_W["type"]  + 2) +
    "+" + "-" * (COL_W["value"] + 2) +
    "+" + "-" * (COL_W["line"]  + 2) +
    "+" + "-" * (COL_W["col"]   + 2) + "+"
)

HEADER = (
    f"| {'TYPE':<{COL_W['type']}} "
    f"| {'VALUE':<{COL_W['value']}} "
    f"| {'LINE':<{COL_W['line']}} "
    f"| {'COL':<{COL_W['col']}} |"
)


def _row(tok_type: str, value: str, line: int, col: int) -> str:
    value_display = repr(value) if value else '""'
    return (
        f"| {tok_type:<{COL_W['type']}} "
        f"| {value_display:<{COL_W['value']}} "
        f"| {line:<{COL_W['line']}} "
        f"| {col:<{COL_W['col']}} |"
    )


def print_tokens(tokens) -> None:
    print(DIVIDER)
    print(HEADER)
    print(DIVIDER)
    for tok in tokens:
        if tok.type in _SKIP_IN_SUMMARY:
            continue
        print(_row(tok.type.name, tok.value, tok.line, tok.column))
    print(DIVIDER)


def print_statistics(tokens) -> None:
    from collections import Counter
    counts = Counter(
        tok.type.name for tok in tokens
        if tok.type not in (TokenType.EOF, TokenType.NEWLINE)
    )
    print("\n📊  Token Statistics")
    print("-" * 36)
    for name, count in sorted(counts.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"  {name:<22} {count:>3}  {bar}")
    print(f"\n  {'TOTAL':<22} {sum(counts.values()):>3}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Determine source
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if not os.path.isfile(filepath):
            print(f"[Error] File not found: {filepath}")
            sys.exit(1)
        with open(filepath, "r", encoding="utf-8") as fh:
            source = fh.read()
        label = filepath
    else:
        # Use bundled sample
        sample_path = os.path.join(os.path.dirname(__file__), "sample.arc")
        with open(sample_path, "r", encoding="utf-8") as fh:
            source = fh.read()
        label = "sample.arc"

    print(f"\n{'='*60}")
    print(f"  🔮  ArcaneScript Lexer  —  source: {label}")
    print(f"{'='*60}\n")

    # Print source
    print("📜  Source Code")
    print("-" * 60)
    for i, line in enumerate(source.splitlines(), 1):
        print(f"  {i:>3} │ {line}")
    print()

    # Lex
    try:
        lexer  = Lexer(source)
        tokens = lexer.tokenize()
    except LexerError as err:
        print(f"\n💥  {err}")
        sys.exit(1)

    # Print token table
    print("🧩  Token Stream")
    print_tokens(tokens)

    # Print stats
    print_statistics(tokens)
    print()


if __name__ == "__main__":
    main()