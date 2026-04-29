"""
Lab 2 - Regular Expressions Generator
Formal Languages & Finite Automata
Variant 1

Regular expressions:
  R1: (a|b)(c|d)E+G?
  R2: P(Q|R|S)T(UV|W|X)*Z+
  R3: 1(0|1)*2(3|4)^5 36

The generator works by parsing each regex into an AST of nodes,
then recursively generating valid strings from that tree.
"""

import random
from dataclasses import dataclass, field
from typing import Union

MAX_REPEAT = 5  # upper limit for * and + quantifiers


# ---------------------------------------------------------------------------
# AST node types
# ---------------------------------------------------------------------------

@dataclass
class Literal:
    """A fixed string, e.g. 'P', 'T', '36'."""
    value: str

@dataclass
class Alternation:
    """One of several alternatives, e.g. (a|b|c)."""
    options: list  # list of AST nodes (each option is itself a node/Concat)

@dataclass
class Concat:
    """A sequence of nodes concatenated together."""
    children: list

@dataclass
class Repeat:
    """
    Quantified repetition of a node.
      min=1, max=1      → exactly once (default, rarely used explicitly)
      min=0, max=1      → ? (optional)
      min=1, max=MAX    → + (one or more)
      min=0, max=MAX    → * (zero or more)
      min=n, max=n      → ^n (exactly n times)
    """
    node: object
    min: int
    max: int


# ---------------------------------------------------------------------------
# Hard-coded ASTs for the three Variant 1 regexes
# (This is the "interpret dynamically" part — the structure is data, not code)
# ---------------------------------------------------------------------------

REGEXES = {
    "R1: (a|b)(c|d)E+G?": Concat([
        Alternation([Literal("a"), Literal("b")]),
        Alternation([Literal("c"), Literal("d")]),
        Repeat(Literal("E"), min=1, max=MAX_REPEAT),
        Repeat(Literal("G"), min=0, max=1),
    ]),

    "R2: P(Q|R|S)T(UV|W|X)*Z+": Concat([
        Literal("P"),
        Alternation([Literal("Q"), Literal("R"), Literal("S")]),
        Literal("T"),
        Repeat(
            Alternation([Literal("UV"), Literal("W"), Literal("X")]),
            min=0, max=MAX_REPEAT
        ),
        Repeat(Literal("Z"), min=1, max=MAX_REPEAT),
    ]),

    "R3: 1(0|1)*2(3|4)^5 36": Concat([
        Literal("1"),
        Repeat(Alternation([Literal("0"), Literal("1")]), min=0, max=MAX_REPEAT),
        Literal("2"),
        Repeat(Alternation([Literal("3"), Literal("4")]), min=5, max=5),
        Literal("36"),
    ]),
}


# ---------------------------------------------------------------------------
# Generator: walk the AST and produce a string + step trace
# ---------------------------------------------------------------------------

def generate(node, steps: list, depth: int = 0) -> str:
    """
    Recursively generate a valid string from an AST node.
    Appends human-readable processing steps to `steps`.
    Returns the generated string fragment.
    """
    indent = "  " * depth

    if isinstance(node, Literal):
        steps.append(f"{indent}Literal '{node.value}' → '{node.value}'")
        return node.value

    if isinstance(node, Concat):
        steps.append(f"{indent}Concatenation of {len(node.children)} parts:")
        result = ""
        for child in node.children:
            result += generate(child, steps, depth + 1)
        steps.append(f"{indent}→ concatenated: '{result}'")
        return result

    if isinstance(node, Alternation):
        choice = random.choice(node.options)
        labels = [_describe(opt) for opt in node.options]
        steps.append(f"{indent}Alternation ({' | '.join(labels)}) → chose: '{_describe(choice)}'")
        return generate(choice, steps, depth + 1)

    if isinstance(node, Repeat):
        count = random.randint(node.min, node.max)
        quantifier = _quantifier_label(node)
        steps.append(f"{indent}Repeat {quantifier} (chose {count} repetition(s)):")
        result = ""
        for i in range(count):
            fragment = generate(node.node, steps, depth + 1)
            result += fragment
        if count == 0:
            steps.append(f"{indent}→ empty (zero repetitions)")
        else:
            steps.append(f"{indent}→ repeated result: '{result}'")
        return result

    raise ValueError(f"Unknown AST node type: {type(node)}")


def _describe(node) -> str:
    """Return a short label for a node (used in step descriptions)."""
    if isinstance(node, Literal):
        return node.value
    if isinstance(node, Alternation):
        return f"({'|'.join(_describe(o) for o in node.options)})"
    if isinstance(node, Concat):
        return "".join(_describe(c) for c in node.children)
    if isinstance(node, Repeat):
        return f"{_describe(node.node)}{_quantifier_label(node)}"
    return "?"


def _quantifier_label(node: Repeat) -> str:
    if node.min == 0 and node.max == 1:
        return "?"
    if node.min == 1 and node.max == MAX_REPEAT:
        return f"+ (1–{MAX_REPEAT})"
    if node.min == 0 and node.max == MAX_REPEAT:
        return f"* (0–{MAX_REPEAT})"
    if node.min == node.max:
        return f"^{node.min}"
    return f"{{{node.min},{node.max}}}"


# ---------------------------------------------------------------------------
# Pretty printer for step traces
# ---------------------------------------------------------------------------

def print_steps(steps: list):
    print("\n  Processing steps:")
    print("  " + "─" * 52)
    for i, step in enumerate(steps, 1):
        print(f"  {i:>2}. {step}")
    print("  " + "─" * 52)


# ---------------------------------------------------------------------------
# Main demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  Formal Languages & Finite Automata — Lab 2")
    print("  Regular Expression Generator  |  Variant 1")
    print("=" * 60)

    for name, ast in REGEXES.items():
        print(f"\n{'─' * 60}")
        print(f"  Regex: {name}")
        print(f"{'─' * 60}")

        # Generate 5 example strings
        print("\n  5 generated examples:")
        examples = []
        for _ in range(5):
            word = generate(ast, steps=[], depth=0)
            examples.append(word)
        print("  {" + ", ".join(examples) + "}")

        # Show detailed step trace for one more generation
        print(f"\n  Detailed trace for one more generation:")
        steps = []
        word = generate(ast, steps=steps, depth=0)
        print_steps(steps)
        print(f"\n  → Final word: '{word}'")

    print(f"\n{'=' * 60}")
    print("  Done.")
    print("=" * 60)


if __name__ == "__main__":
    main()