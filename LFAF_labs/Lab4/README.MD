# Laboratory Work No. 2 — Regular Expressions

**Course:** Formal Languages & Finite Automata  
**Student:** Eftode Andrei, FAF-242  
**Teacher:** Cretu D.  
**Date:** March 2026

---

## 1. Overview

This laboratory work focuses on regular expressions — their structure, meaning, and practical use in generating valid strings that conform to them. The goal was not just to understand what a given regex matches, but to actually write code that can interpret and generate valid words from it dynamically.

Variant 1 was assigned, which comes with three regular expressions:

```
R1: (a|b)(c|d)E+G?
R2: P(Q|R|S)T(UV|W|X)*Z+
R3: 1(0|1)*2(3|4)^5 36
```

---

## 2. What Are Regular Expressions?

A regular expression (regex) is a formal way to describe a set of strings — called a language — using a compact symbolic notation. They are a fundamental concept in formal language theory and are directly tied to finite automata: every regular expression corresponds to a finite automaton, and vice versa.

In practice, regular expressions are used everywhere: text search and validation (email addresses, phone numbers), lexers and tokenizers in compilers, search engines, network packet filtering, and much more.

The main building blocks are:

- **Literals** — individual symbols like `a`, `P`, `3`
- **Alternation** `(x|y)` — pick one option from a set
- **Concatenation** — placing tokens in sequence
- **Kleene star** `*` — zero or more repetitions
- **Plus** `+` — one or more repetitions
- **Optional** `?` — zero or one occurrence
- **Exact repetition** `^n` — exactly *n* repetitions

---

## 3. Implementation

### 3.1 Design Approach

The core idea was to represent each regular expression as an **Abstract Syntax Tree (AST)**, where every node in the tree corresponds to a part of the regex. Generation then becomes a simple recursive traversal of that tree.

Four node types were defined:

```python
@dataclass
class Literal:
    value: str

@dataclass
class Alternation:
    options: list  # list of child nodes

@dataclass
class Concat:
    children: list

@dataclass
class Repeat:
    node: object
    min: int
    max: int
```

This means the structure of each regex is expressed as **data**, not as hardcoded control flow. Changing a regex means changing the tree — the generator itself stays the same.

### 3.2 The Generator

The `generate()` function is a single recursive function that walks any AST node:

```python
def generate(node, steps, depth=0):
    if isinstance(node, Literal):
        return node.value
    if isinstance(node, Concat):
        return "".join(generate(c, steps, depth+1) for c in node.children)
    if isinstance(node, Alternation):
        choice = random.choice(node.options)
        return generate(choice, steps, depth+1)
    if isinstance(node, Repeat):
        count = random.randint(node.min, node.max)
        return "".join(generate(node.node, steps, depth+1) for _ in range(count))
```

Each call appends a human-readable step to a `steps` list, so the full processing trace is available after generation.

### 3.3 Handling the Three Regexes

**R1: `(a|b)(c|d)E+G?`**

```python
Concat([
    Alternation([Literal("a"), Literal("b")]),
    Alternation([Literal("c"), Literal("d")]),
    Repeat(Literal("E"), min=1, max=5),
    Repeat(Literal("G"), min=0, max=1),
])
```

Generates strings like: `acEG`, `bdEEE`, `adE`, `bcEEEEEG`

**R2: `P(Q|R|S)T(UV|W|X)*Z+`**

```python
Concat([
    Literal("P"),
    Alternation([Literal("Q"), Literal("R"), Literal("S")]),
    Literal("T"),
    Repeat(Alternation([Literal("UV"), Literal("W"), Literal("X")]), min=0, max=5),
    Repeat(Literal("Z"), min=1, max=5),
])
```

Generates strings like: `PQTUVUVZ`, `PRTWWWWZZ`, `PSTZ`

**R3: `1(0|1)*2(3|4)^5 36`**

```python
Concat([
    Literal("1"),
    Repeat(Alternation([Literal("0"), Literal("1")]), min=0, max=5),
    Literal("2"),
    Repeat(Alternation([Literal("3"), Literal("4")]), min=5, max=5),
    Literal("36"),
])
```

The `^5` notation is treated as `min=5, max=5` in the `Repeat` node, so it always produces exactly 5 digits from (3|4). Generates strings like: `1023333336`, `1124444436`, `123434336`

### 3.4 Repetition Limit

As specified, the upper bound for `*` and `+` quantifiers was capped at 5 to avoid extremely long output:

```python
MAX_REPEAT = 5
```

This constant is used in every `Repeat` node that would otherwise be unbounded.

### 3.5 Processing Steps (Bonus)

The `generate()` function builds a trace as a side effect. Each recursive call appends a line describing what it did and what value it produced. The trace is indented by recursion depth, making it easy to follow:

```
 1. Concatenation of 4 parts:
 2.   Alternation (a | b) → chose: 'b'
 3.     Literal 'b' → 'b'
 4.   Alternation (c | d) → chose: 'c'
 5.     Literal 'c' → 'c'
 6.   Repeat + (1–5) (chose 3 repetition(s)):
 7.     Literal 'E' → 'E'
 8.     Literal 'E' → 'E'
 9.     Literal 'E' → 'E'
10.   → repeated result: 'EEE'
11.   Repeat ? (chose 0 repetition(s)):
12.   → empty (zero repetitions)
13. → concatenated: 'bcEEE'
```

---

## 4. Running the Code

```bash
python regex_generator.py
```

Sample output:

```
============================================================
  Formal Languages & Finite Automata — Lab 2
  Regular Expression Generator  |  Variant 1
============================================================

────────────────────────────────────────────────────────────
  Regex: R1: (a|b)(c|d)E+G?
────────────────────────────────────────────────────────────

  5 generated examples:
  {acEEEEG, bcEEE, bcE, adEG, acEEEE}

────────────────────────────────────────────────────────────
  Regex: R2: P(Q|R|S)T(UV|W|X)*Z+
────────────────────────────────────────────────────────────

  5 generated examples:
  {PRTXWXXZZZZ, PQTWUVZ, PQTXUVZZ, PRTUVUVUVXWZZ, PRTZZZZZ}

────────────────────────────────────────────────────────────
  Regex: R3: 1(0|1)*2(3|4)^5 36
────────────────────────────────────────────────────────────

  5 generated examples:
  {100123343436, 1023333336, 11023333436, 100023333336, 124433436}
```

---

## 5. Difficulties Encountered

**Understanding the `^5` notation.** This one took a moment — in most regex flavors, `{5}` is the standard notation for exact repetition, but the lab uses `^5` as a superscript. I treated it as `min=max=5` in the `Repeat` node, which maps cleanly onto the same data structure used for `+` and `*`.

**Making it actually dynamic.** The temptation when you have only three fixed regexes is to just write three functions, one per regex, with hardcoded logic. But the lab specifically asks for dynamic interpretation. The AST approach solves this — adding a new regex just means defining its tree. The generator code doesn't change at all.

**Keeping the step trace readable.** Initially the steps were a flat list with no indication of nesting, which made it hard to follow for deeply nested trees like R2. Adding indentation based on recursion depth (the `depth` parameter) fixed this and made the trace much easier to read.

**R2's alternation includes a two-character option.** `(UV|W|X)` — `UV` is two characters but is treated as a single alternative. This is handled naturally in the AST since `Literal("UV")` is just a node whose value happens to be two characters. No special casing needed.

---

## 6. Conclusions

This lab was a good exercise in thinking about the structure of regular expressions more carefully than you usually would when just using them for text matching. Building an AST and walking it recursively made the generation problem feel natural and general — the same code handles all three regexes without modification.

The main takeaway is that regular expressions are not just patterns for matching text; they are formal descriptions of languages, and you can do things with them beyond matching — like generating members of the language they describe. The AST representation makes the structure explicit, which is useful both for generation and for the kind of analysis done in a formal languages course.

The step trace was a useful addition: it makes the generation process transparent and serves as a nice illustration of how the regex is being consumed left to right, with each operator resolved in order.

---

## 7. References

1. Sipser, M. — *Introduction to the Theory of Computation*, 3rd ed.
2. Hopcroft, Motwani, Ullman — *Introduction to Automata Theory, Languages, and Computation*
3. Python `random` module documentation — https://docs.python.org/3/library/random.html
4. Course materials — Formal Languages & Finite Automata, FAF, TUM