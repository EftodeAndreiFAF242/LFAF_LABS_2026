# Parser & Abstract Syntax Tree

**Course:** Formal Languages & Finite Automata  
**Laboratory Work #6**  
**Author:** Cretu Dumitru  
**Student:** Eftode Andrei, FAF-242  
**Date:** May 2026

---

## Theory

Parsing is the process of analyzing a sequence of tokens to determine its grammatical structure relative to a formal grammar. It is a fundamental step in compilers, interpreters, and any tool that needs to understand structured text.

A **Parse Tree** (also called a concrete syntax tree) reflects the exact grammar rules applied during parsing, including all intermediate nodes. An **Abstract Syntax Tree (AST)**, by contrast, strips away irrelevant details (such as parentheses and punctuation) and retains only the semantic structure of the input — making it more compact and useful for subsequent stages like interpretation, optimization, or code generation.

A **recursive-descent parser** is a top-down parser that implements each grammar rule as a function. It is predictive (no backtracking) when the grammar is LL(1) or close to it, and is simple enough to write by hand. Each grammar rule — expression, statement, block, and so on — maps directly to a method in the parser class.

---

## Objectives

1. Get familiar with parsing and how it can be implemented programmatically.
2. Understand the concept and structure of an Abstract Syntax Tree.
3. Extend the previous lab work (lexer) by:
   - Introducing a `TokenType` enum to categorize tokens.
   - Using regular expressions to identify token types.
   - Implementing AST data structures for the language grammar.
   - Implementing a simple recursive-descent parser.

---

## Implementation

The project is organized into a single self-contained Python file (`src/main.py`) with four distinct layers:

### 1. Token Types (`TokenType`)

Defined as a Python `Enum`, `TokenType` covers all categories a token can belong to: integer and float literals, strings, booleans, identifiers, keywords (`let`, `if`, `else`, `while`, `return`, `func`, `print`), arithmetic and logical operators, comparison operators, and delimiter characters.

```python
class TokenType(Enum):
    INTEGER = auto()
    FLOAT   = auto()
    STRING  = auto()
    BOOLEAN = auto()
    IDENTIFIER = auto()
    LET = auto()
    # ... etc.
```

### 2. Lexer

The `Lexer` class tokenizes raw source code into a flat list of `Token` objects. Each token carries its type, value, line number, and column — useful for error reporting.

Token recognition is driven by a priority-ordered list of compiled regular expressions:

```python
TOKEN_PATTERNS = [
    (r'\d+\.\d+',      TokenType.FLOAT),
    (r'\d+',           TokenType.INTEGER),
    (r'"[^"]*"',       TokenType.STRING),
    (r'[A-Za-z_]\w*', TokenType.IDENTIFIER),
    (r'==',            TokenType.EQ),
    # ... etc.
]
```

Longer patterns (like `==`, `<=`) are listed before shorter ones (`=`, `<`) to avoid incorrect early matches. After matching an identifier, the lexer checks a `KEYWORDS` dictionary to promote it to the appropriate keyword token type. Line comments (`//`) are skipped during scanning.

### 3. AST Node Hierarchy

All AST nodes extend a base `ASTNode` class that implements the **Visitor pattern** via an `accept` method:

```python
@dataclass
class ASTNode:
    def accept(self, visitor):
        method = f"visit_{type(self).__name__}"
        return getattr(visitor, method, visitor.generic_visit)(self)
```

The full set of node types covers:

| Node | Description |
|---|---|
| `Program` | Root of the tree; holds a list of top-level statements |
| `VarDeclaration` | `let name = expr;` |
| `Assignment` | `name = expr;` (re-assignment) |
| `FunctionDeclaration` | `func name(params) { body }` |
| `ReturnStatement` | `return expr;` |
| `IfStatement` | `if (cond) { ... } else { ... }` |
| `WhileStatement` | `while (cond) { ... }` |
| `PrintStatement` | `print(expr);` |
| `Block` | A `{ }` enclosed list of statements |
| `BinaryOp` | Left-operand, operator symbol, right operand |
| `UnaryOp` | Operator and single operand |
| `FunctionCall` | Function name and argument list |
| `Identifier` | A variable name reference |
| `Literal` | An integer, float, string, or boolean value |

### 4. Parser

`Parser` is a hand-written recursive-descent parser. Each grammar rule is implemented as a dedicated method. The grammar it recognizes:

```
program     → statement* EOF
statement   → varDecl | funcDecl | ifStmt | whileStmt
            | returnStmt | printStmt | exprStmt
varDecl     → "let" IDENT "=" expression ";"
funcDecl    → "func" IDENT "(" params? ")" block
ifStmt      → "if" "(" expression ")" block ( "else" block )?
whileStmt   → "while" "(" expression ")" block
returnStmt  → "return" expression? ";"
printStmt   → "print" "(" expression ")" ";"
block       → "{" statement* "}"
expression  → assignment
assignment  → IDENT "=" assignment | logicOr
logicOr     → logicAnd ( "||" logicAnd )*
logicAnd    → equality ( "&&" equality )*
equality    → comparison ( ( "==" | "!=" ) comparison )*
comparison  → term ( ( "<" | ">" | "<=" | ">=" ) term )*
term        → factor ( ( "+" | "-" ) factor )*
factor      → unary ( ( "*" | "/" | "%" ) unary )*
unary       → ( "!" | "-" ) unary | primary
primary     → INT | FLOAT | STRING | BOOL | IDENT | call | "(" expression ")"
call        → IDENT "(" args? ")"
```

Operator precedence is enforced by the call chain — lower-precedence rules delegate to higher-precedence ones. An `ASTPrinter` visitor then walks the resulting tree and prints it with indentation for human-readable inspection.

---

## Results

Running `python src/main.py` on the built-in sample program (which includes a recursive `factorial` function, a `while` loop, and conditional logic) produces two outputs: a token list and the final AST.

**Sample token output (excerpt):**
```
Token(FUNC, 'func', 3:1)
Token(IDENTIFIER, 'factorial', 3:6)
Token(LPAREN, '(', 3:15)
Token(IDENTIFIER, 'n', 3:16)
Token(RPAREN, ')', 3:17)
...
```

**Sample AST output (excerpt):**
```
Program
  FuncDecl: factorial(n)
    Block
      If
        [condition]
          BinaryOp: '<='
            Identifier: n
            Literal(int): 1
        [then]
          Block
            Return
              Literal(int): 1
      Return
        BinaryOp: '*'
          Identifier: n
          Call: factorial
            BinaryOp: '-'
              Identifier: n
              Literal(int): 1
  VarDecl: x
    Literal(int): 5
  ...
```

The tree correctly captures the recursive structure of `factorial`, the loop, and the conditional branches — each in its own abstraction layer.

---

## Conclusions

This lab work brought together lexical analysis from the previous assignment and extended it into a full parsing pipeline. Defining `TokenType` as an enum made the lexer more structured and made pattern matching across the codebase straightforward. Using regular expressions for tokenization kept the lexer concise while handling all token categories reliably.

The recursive-descent parser turned out to be a natural fit for the language grammar: each production rule maps cleanly to a method, and the call stack mirrors the nesting structure of the source. The resulting AST is compact and easy to traverse using the visitor pattern, which separates tree structure from the operations performed on it.

Overall, the implementation demonstrates that even a simple hand-written parser can handle a reasonably expressive language — including recursion, loops, conditionals, and multiple data types — with predictable behavior and readable code.

---

## References

1. Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Addison-Wesley.
2. Nystrom, R. (2021). *Crafting Interpreters*. Retrieved from https://craftinginterpreters.com
3. Course materials — Formal Languages & Finite Automata, Technical University of Moldova.