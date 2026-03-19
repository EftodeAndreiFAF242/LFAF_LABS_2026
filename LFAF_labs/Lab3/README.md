#  ArcaneScript Lexer

**Author:** Eftode Andrei  
**Course:** Formal Languages & Finite Automata  
**Topic:** Lexer / Scanner  
**Lab:** Laboratory Work #3

---

## Overview

This project implements a **lexical analyzer (lexer)** for a custom-designed language called **ArcaneScript** — a magic-themed scripting language. The lexer takes raw ArcaneScript source code as input and produces a structured stream of tokens, which is the foundational first stage of any compiler or interpreter pipeline.

Lexical analysis is the process of reading a sequence of characters and grouping them into meaningful units called **lexemes**, then classifying each lexeme into a **token type** (e.g. keyword, integer, operator). The lexer does not understand the grammar or meaning of a program — it only identifies and categorizes the smallest meaningful units.

The difference between a **lexeme** and a **token** is important:
- A **lexeme** is the raw string extracted from the source, for example `75.5` or `if_cursed`.
- A **token** is the categorized result — it pairs the lexeme with a type like `FLOAT` or `IF_CURSED`, and optionally stores metadata such as line and column numbers.

---

## What is ArcaneScript?

ArcaneScript is a fully custom scripting language built around a **fantasy / spell-casting theme**. Every keyword, construct, and operator in the language is modelled after the idea of a wizard writing spells and incantations rather than plain code. The goal was to design a language rich enough to demonstrate all major token categories a real lexer must handle, while being original and distinct from the usual calculator or arithmetic expression examples.

ArcaneScript supports:

- **Variable declaration** using `summon` — like declaring a new entity into existence
- **Function definition** using `cast` — casting a named spell that accepts parameters
- **Return statements** using `banish` — banishing a value back out of a spell
- **Conditionals** using `if_cursed` and `else_ward` — branching based on whether a condition is "cursed" (true)
- **Loops** using `while_enchanted` — repeating a block while an enchantment holds
- **Output** using `inscribe` — inscribing a message into the world (printing to screen)
- **Boolean literals** `true_rune` and `false_rune` — runes representing truth and falsehood
- **Comments** starting with `~~` — anything after `~~` on a line is ignored by the lexer
- **All standard arithmetic**: `+`, `-`, `*`, `/`, `%`, and `**` for exponentiation
- **All standard comparisons**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Logical operators**: `&&` (and), `||` (or), `!` (not)
- **Integer and float literals**, **string literals** (single or double quoted)

### Keyword Reference

| ArcaneScript Keyword  | Equivalent in conventional languages | Meaning                          |
|-----------------------|---------------------------------------|----------------------------------|
| `summon`              | `var` / `let`                         | Declare a variable               |
| `cast`                | `def` / `function`                    | Define a function                |
| `banish`              | `return`                              | Return a value from a function   |
| `if_cursed`           | `if`                                  | Conditional branch               |
| `else_ward`           | `else`                                | Fallback branch                  |
| `while_enchanted`     | `while`                               | Loop while condition holds       |
| `inscribe`            | `print`                               | Output a value                   |
| `true_rune`           | `true`                                | Boolean true                     |
| `false_rune`          | `false`                               | Boolean false                    |
| `~~ text`             | `// text`                             | Single-line comment              |

---

## ArcaneScript in Action

Below is a complete example program written in ArcaneScript. It demonstrates variables, floats, strings, booleans, arithmetic with exponentiation, a function with conditionals, a loop with logical operators, and output statements.

```
~~ ArcaneScript Sample Program
~~ Demonstrates all major token categories

~~ Variable declarations
summon health = 100;
summon mana   = 75.5;
summon name   = "Eftode Andrei";
summon alive  = true_rune;

~~ Arithmetic & power operator
summon damage = 3 ** 2 + health * 0.1 - mana / 5.0;

~~ Function definition
cast heal(target, amount) {
    summon new_hp = target + amount;
    if_cursed (new_hp > 100) {
        banish 100;
    }
    else_ward {
        banish new_hp;
    }
}

~~ Loop with logical operator
summon counter = 5;
while_enchanted (counter != 0 && alive == true_rune) {
    inscribe("Casting spell...");
    summon counter = counter - 1;
}

~~ Function call & comparison chain
summon result = heal(health, 25);
if_cursed (result >= 100) {
    inscribe("Fully healed!");
}
else_ward {
    inscribe("Still wounded.");
}
```

When the lexer processes this program it produces **135 tokens** spanning all categories — keywords, identifiers, integers, floats, strings, operators, delimiters, and comments — demonstrating the full range of lexical analysis.

---

## Project Structure

```
arcanescript_lexer/
│
├── arc_token.py        # Token class, TokenType enum, KEYWORDS map
├── lexer.py            # Core Lexer class — scans source into tokens
├── main.py             # Entry point — runs the lexer and prints results
├── sample.arc          # Demo ArcaneScript source file
└── test_lexer.py       # 25 unit tests covering all token categories
```

---

## Token Categories

The lexer recognises the following token types, grouped by category:

| Category              | Token Types |
|-----------------------|-------------|
| **Literals**          | `INTEGER`, `FLOAT`, `STRING` |
| **Keywords**          | `CAST`, `SUMMON`, `BANISH`, `IF_CURSED`, `ELSE_WARD`, `WHILE_ENCHANTED`, `INSCRIBE`, `TRUE_RUNE`, `FALSE_RUNE` |
| **Identifiers**       | `IDENTIFIER` — any variable or function name |
| **Arithmetic**        | `PLUS`, `MINUS`, `MULTIPLY`, `DIVIDE`, `MODULO`, `POWER` |
| **Comparison**        | `EQ`, `NEQ`, `LT`, `GT`, `LTE`, `GTE` |
| **Logical**           | `AND_BIND`, `OR_WEAVE`, `NOT_DISPEL` |
| **Assignment**        | `ASSIGN` |
| **Delimiters**        | `LPAREN`, `RPAREN`, `LBRACE`, `RBRACE`, `LBRACKET`, `RBRACKET`, `COMMA`, `SEMICOLON`, `COLON`, `DOT` |
| **Special**           | `COMMENT`, `NEWLINE`, `EOF`, `UNKNOWN` |

---

## How the Lexer Works

The `Lexer` class iterates over the source string one character at a time using a position pointer (`self.pos`). At each step it calls `_scan_token()`, which inspects the current character and dispatches to the appropriate reader:

1. **Whitespace** — spaces, tabs, and carriage returns are silently skipped; they act as delimiters but produce no tokens.
2. **Newlines** — produce a `NEWLINE` token and increment the internal line counter, which is used for error reporting.
3. **Comments (`~~`)** — when two consecutive `~` characters are found, `_read_comment()` consumes everything until the end of the line and emits a single `COMMENT` token.
4. **String literals** — opening `"` or `'` triggers `_read_string()`, which consumes characters until the matching closing quote, handling backslash escape sequences along the way. An unterminated string (newline before closing quote) raises a `LexerError`.
5. **Number literals** — any digit triggers `_read_number()`, which first reads integer digits, then checks for a `.` followed by more digits to decide between `INTEGER` and `FLOAT`.
6. **Identifiers and keywords** — any letter or underscore triggers `_read_identifier()`, which reads the full alphanumeric word and then looks it up in the `KEYWORDS` dictionary. If found, the keyword token type is used; otherwise it becomes an `IDENTIFIER`.
7. **Two-character operators** — before checking single characters, the lexer uses `_peek()` to look one character ahead. This allows it to correctly distinguish `=` (assign) from `==` (equality), `!` from `!=`, `<` from `<=`, `>` from `>=`, `&` from `&&`, `|` from `||`, and `*` from `**`.
8. **Single-character tokens** — all remaining symbols are matched against a lookup dictionary mapping characters to token types.
9. **Unknown characters** — anything not matched produces an `UNKNOWN` token instead of crashing, making the lexer fault-tolerant.

Every token carries four fields: `type`, `value` (the raw lexeme string), `line`, and `column` — enabling pinpoint error messages in later compilation stages.

---

## How to Run

### Run the built-in demo

```bash
python main.py
```

This lexes `sample.arc` and prints the full token table plus a statistics breakdown of every token type found.

### Lex a custom file

```bash
python main.py path/to/your_file.arc
```

### Run the unit tests

```bash
python -m unittest test_lexer -v
```

Expected output: **25 tests, 0 failures.**

---

## Requirements

- Python **3.10+**
- No third-party dependencies — standard library only
- `unittest` is used for testing (built into Python, no installation needed)

---

## Key Concepts Demonstrated

- **Lexeme vs Token** — the lexer extracts raw lexemes (e.g. `75.5`) and assigns them a token type (`FLOAT`), separating the actual value from its category.
- **Finite automaton behaviour** — the character-by-character dispatch with one-character lookahead mirrors how a deterministic finite automaton (DFA) transitions between states while reading an input tape.
- **Line & column tracking** — every token carries its exact source location, enabling precise error messages that point to the right place in the source file.
- **Keyword recognition** — identifiers are read fully first, then checked against a keyword table. This means `summons` correctly becomes an `IDENTIFIER` while `summon` becomes a keyword — there is no ambiguity.
- **Lookahead** — the `_peek()` method reads one character ahead without consuming it, which is essential for correctly identifying two-character operators like `==`, `!=`, `**`, `&&`, and `||`.
- **Error handling** — `LexerError` is raised with line and column information when the source is malformed, for example when a string literal is never closed.

---

## Conclusion

This laboratory work successfully delivered a fully functional lexical analyzer for ArcaneScript — a custom-designed, magic-themed scripting language. The implementation covers all core responsibilities of a real-world lexer: character-by-character scanning, one-character lookahead for multi-character operators, keyword disambiguation, string and number literal parsing, comment handling, and precise source location tracking on every emitted token.




