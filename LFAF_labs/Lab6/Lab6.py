"""
Lab 4: Parser & Abstract Syntax Tree (AST)
Course: Formal Languages & Finite Automata
Author: Cretu Dumitru
Student: Eftode Andrei, FAF-242
"""

import re
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Optional, Any


# ─────────────────────────────────────────────
#  TOKEN TYPES
# ─────────────────────────────────────────────

class TokenType(Enum):
    # Literals
    INTEGER     = auto()
    FLOAT       = auto()
    STRING      = auto()
    BOOLEAN     = auto()

    # Identifiers & keywords
    IDENTIFIER  = auto()
    LET         = auto()
    IF          = auto()
    ELSE        = auto()
    WHILE       = auto()
    RETURN      = auto()
    FUNC        = auto()
    PRINT       = auto()

    # Operators
    PLUS        = auto()
    MINUS       = auto()
    STAR        = auto()
    SLASH       = auto()
    PERCENT     = auto()
    ASSIGN      = auto()
    EQ          = auto()
    NEQ         = auto()
    LT          = auto()
    GT          = auto()
    LEQ         = auto()
    GEQ         = auto()
    AND         = auto()
    OR          = auto()
    NOT         = auto()

    # Delimiters
    LPAREN      = auto()
    RPAREN      = auto()
    LBRACE      = auto()
    RBRACE      = auto()
    COMMA       = auto()
    SEMICOLON   = auto()
    COLON       = auto()

    # Special
    EOF         = auto()


# ─────────────────────────────────────────────
#  TOKEN
# ─────────────────────────────────────────────

@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


# ─────────────────────────────────────────────
#  LEXER
# ─────────────────────────────────────────────

KEYWORDS = {
    "let":    TokenType.LET,
    "if":     TokenType.IF,
    "else":   TokenType.ELSE,
    "while":  TokenType.WHILE,
    "return": TokenType.RETURN,
    "func":   TokenType.FUNC,
    "print":  TokenType.PRINT,
    "true":   TokenType.BOOLEAN,
    "false":  TokenType.BOOLEAN,
}

TOKEN_PATTERNS = [
    (r'\d+\.\d+',             TokenType.FLOAT),
    (r'\d+',                  TokenType.INTEGER),
    (r'"[^"]*"',              TokenType.STRING),
    (r'[A-Za-z_]\w*',        TokenType.IDENTIFIER),
    (r'==',                   TokenType.EQ),
    (r'!=',                   TokenType.NEQ),
    (r'<=',                   TokenType.LEQ),
    (r'>=',                   TokenType.GEQ),
    (r'&&',                   TokenType.AND),
    (r'\|\|',                 TokenType.OR),
    (r'!',                    TokenType.NOT),
    (r'\+',                   TokenType.PLUS),
    (r'-',                    TokenType.MINUS),
    (r'\*',                   TokenType.STAR),
    (r'/',                    TokenType.SLASH),
    (r'%',                    TokenType.PERCENT),
    (r'=',                    TokenType.ASSIGN),
    (r'<',                    TokenType.LT),
    (r'>',                    TokenType.GT),
    (r'\(',                   TokenType.LPAREN),
    (r'\)',                   TokenType.RPAREN),
    (r'\{',                   TokenType.LBRACE),
    (r'\}',                   TokenType.RBRACE),
    (r',',                    TokenType.COMMA),
    (r';',                    TokenType.SEMICOLON),
    (r':',                    TokenType.COLON),
]

COMPILED = [(re.compile(p), t) for p, t in TOKEN_PATTERNS]


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def error(self, ch: str):
        raise SyntaxError(f"Unexpected character {ch!r} at {self.line}:{self.column}")

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            # Skip whitespace
            if self.source[self.pos] in ' \t\r':
                self._advance()
                continue
            if self.source[self.pos] == '\n':
                self.line += 1
                self.column = 1
                self.pos += 1
                continue
            # Skip line comments
            if self.source[self.pos:self.pos + 2] == '//':
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self.pos += 1
                continue

            matched = False
            for regex, ttype in COMPILED:
                m = regex.match(self.source, self.pos)
                if m:
                    value = m.group(0)
                    col = self.column
                    # Promote identifier to keyword if applicable
                    if ttype == TokenType.IDENTIFIER and value in KEYWORDS:
                        ttype = KEYWORDS[value]
                    # Convert literal values
                    if ttype == TokenType.INTEGER:
                        value = int(value)
                    elif ttype == TokenType.FLOAT:
                        value = float(value)
                    elif ttype == TokenType.BOOLEAN:
                        value = value == "true"
                    elif ttype == TokenType.STRING:
                        value = value[1:-1]  # strip quotes

                    self.tokens.append(Token(ttype, value, self.line, col))
                    self.column += len(m.group(0))
                    self.pos = m.end()
                    matched = True
                    break

            if not matched:
                self.error(self.source[self.pos])

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    def _advance(self):
        self.pos += 1
        self.column += 1


# ─────────────────────────────────────────────
#  AST NODES
# ─────────────────────────────────────────────

@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    def accept(self, visitor):
        method = f"visit_{type(self).__name__}"
        return getattr(visitor, method, visitor.generic_visit)(self)


@dataclass
class Program(ASTNode):
    statements: List[ASTNode]


@dataclass
class VarDeclaration(ASTNode):
    name: str
    value: ASTNode


@dataclass
class Assignment(ASTNode):
    name: str
    value: ASTNode


@dataclass
class FunctionDeclaration(ASTNode):
    name: str
    params: List[str]
    body: "Block"


@dataclass
class ReturnStatement(ASTNode):
    value: Optional[ASTNode]


@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_branch: "Block"
    else_branch: Optional["Block"]


@dataclass
class WhileStatement(ASTNode):
    condition: ASTNode
    body: "Block"


@dataclass
class PrintStatement(ASTNode):
    value: ASTNode


@dataclass
class Block(ASTNode):
    statements: List[ASTNode]


@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode


@dataclass
class UnaryOp(ASTNode):
    op: str
    operand: ASTNode


@dataclass
class FunctionCall(ASTNode):
    name: str
    args: List[ASTNode]


@dataclass
class Identifier(ASTNode):
    name: str


@dataclass
class Literal(ASTNode):
    value: Any
    kind: str  # "int", "float", "string", "bool"


# ─────────────────────────────────────────────
#  PARSER
# ─────────────────────────────────────────────

class ParseError(Exception):
    pass


class Parser:
    """
    Recursive-descent parser.

    Grammar (simplified):
        program        → statement* EOF
        statement      → varDecl | funcDecl | ifStmt | whileStmt
                       | returnStmt | printStmt | exprStmt
        varDecl        → "let" IDENT "=" expression ";"
        funcDecl       → "func" IDENT "(" params? ")" block
        ifStmt         → "if" "(" expression ")" block ( "else" block )?
        whileStmt      → "while" "(" expression ")" block
        returnStmt     → "return" expression? ";"
        printStmt      → "print" "(" expression ")" ";"
        exprStmt       → expression ";"
        block          → "{" statement* "}"
        expression     → assignment
        assignment     → IDENT "=" assignment | logicOr
        logicOr        → logicAnd ( "||" logicAnd )*
        logicAnd       → equality ( "&&" equality )*
        equality       → comparison ( ( "==" | "!=" ) comparison )*
        comparison     → term ( ( "<" | ">" | "<=" | ">=" ) term )*
        term           → factor ( ( "+" | "-" ) factor )*
        factor         → unary ( ( "*" | "/" | "%" ) unary )*
        unary          → ( "!" | "-" ) unary | primary
        primary        → INT | FLOAT | STRING | BOOL | IDENT | call | "(" expression ")"
        call           → IDENT "(" args? ")"
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # ── helpers ──────────────────────────────

    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def check(self, *types: TokenType) -> bool:
        return self.current().type in types

    def match(self, *types: TokenType) -> Optional[Token]:
        if self.check(*types):
            return self.advance()
        return None

    def expect(self, ttype: TokenType, msg: str = "") -> Token:
        if self.check(ttype):
            return self.advance()
        tok = self.current()
        raise ParseError(
            msg or f"Expected {ttype.name}, got {tok.type.name} ({tok.value!r}) at {tok.line}:{tok.column}"
        )

    # ── grammar rules ─────────────────────────

    def parse(self) -> Program:
        stmts = []
        while not self.check(TokenType.EOF):
            stmts.append(self.statement())
        return Program(statements=stmts)

    def statement(self) -> ASTNode:
        if self.check(TokenType.LET):
            return self.var_decl()
        if self.check(TokenType.FUNC):
            return self.func_decl()
        if self.check(TokenType.IF):
            return self.if_stmt()
        if self.check(TokenType.WHILE):
            return self.while_stmt()
        if self.check(TokenType.RETURN):
            return self.return_stmt()
        if self.check(TokenType.PRINT):
            return self.print_stmt()
        return self.expr_stmt()

    def var_decl(self) -> VarDeclaration:
        self.expect(TokenType.LET)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        val = self.expression()
        self.expect(TokenType.SEMICOLON)
        return VarDeclaration(name=name, value=val)

    def func_decl(self) -> FunctionDeclaration:
        self.expect(TokenType.FUNC)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)
        params = []
        if not self.check(TokenType.RPAREN):
            params.append(self.expect(TokenType.IDENTIFIER).value)
            while self.match(TokenType.COMMA):
                params.append(self.expect(TokenType.IDENTIFIER).value)
        self.expect(TokenType.RPAREN)
        body = self.block()
        return FunctionDeclaration(name=name, params=params, body=body)

    def if_stmt(self) -> IfStatement:
        self.expect(TokenType.IF)
        self.expect(TokenType.LPAREN)
        cond = self.expression()
        self.expect(TokenType.RPAREN)
        then = self.block()
        else_ = None
        if self.match(TokenType.ELSE):
            else_ = self.block()
        return IfStatement(condition=cond, then_branch=then, else_branch=else_)

    def while_stmt(self) -> WhileStatement:
        self.expect(TokenType.WHILE)
        self.expect(TokenType.LPAREN)
        cond = self.expression()
        self.expect(TokenType.RPAREN)
        body = self.block()
        return WhileStatement(condition=cond, body=body)

    def return_stmt(self) -> ReturnStatement:
        self.expect(TokenType.RETURN)
        val = None
        if not self.check(TokenType.SEMICOLON):
            val = self.expression()
        self.expect(TokenType.SEMICOLON)
        return ReturnStatement(value=val)

    def print_stmt(self) -> PrintStatement:
        self.expect(TokenType.PRINT)
        self.expect(TokenType.LPAREN)
        val = self.expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        return PrintStatement(value=val)

    def expr_stmt(self) -> ASTNode:
        expr = self.expression()
        self.expect(TokenType.SEMICOLON)
        return expr

    def block(self) -> Block:
        self.expect(TokenType.LBRACE)
        stmts = []
        while not self.check(TokenType.RBRACE) and not self.check(TokenType.EOF):
            stmts.append(self.statement())
        self.expect(TokenType.RBRACE)
        return Block(statements=stmts)

    # ── expressions ───────────────────────────

    def expression(self) -> ASTNode:
        return self.assignment()

    def assignment(self) -> ASTNode:
        if (self.check(TokenType.IDENTIFIER)
                and self.peek().type == TokenType.ASSIGN):
            name = self.advance().value
            self.advance()  # consume '='
            val = self.assignment()
            return Assignment(name=name, value=val)
        return self.logic_or()

    def logic_or(self) -> ASTNode:
        node = self.logic_and()
        while self.check(TokenType.OR):
            op = self.advance().value
            right = self.logic_and()
            node = BinaryOp(left=node, op="||", right=right)
        return node

    def logic_and(self) -> ASTNode:
        node = self.equality()
        while self.check(TokenType.AND):
            self.advance()
            right = self.equality()
            node = BinaryOp(left=node, op="&&", right=right)
        return node

    def equality(self) -> ASTNode:
        node = self.comparison()
        while self.check(TokenType.EQ, TokenType.NEQ):
            op = self.advance().type
            sym = "==" if op == TokenType.EQ else "!="
            right = self.comparison()
            node = BinaryOp(left=node, op=sym, right=right)
        return node

    def comparison(self) -> ASTNode:
        node = self.term()
        _map = {TokenType.LT: "<", TokenType.GT: ">",
                TokenType.LEQ: "<=", TokenType.GEQ: ">="}
        while self.current().type in _map:
            sym = _map[self.advance().type]
            right = self.term()
            node = BinaryOp(left=node, op=sym, right=right)
        return node

    def term(self) -> ASTNode:
        node = self.factor()
        while self.check(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().type
            sym = "+" if op == TokenType.PLUS else "-"
            right = self.factor()
            node = BinaryOp(left=node, op=sym, right=right)
        return node

    def factor(self) -> ASTNode:
        node = self.unary()
        _map = {TokenType.STAR: "*", TokenType.SLASH: "/", TokenType.PERCENT: "%"}
        while self.current().type in _map:
            sym = _map[self.advance().type]
            right = self.unary()
            node = BinaryOp(left=node, op=sym, right=right)
        return node

    def unary(self) -> ASTNode:
        if self.check(TokenType.NOT):
            self.advance()
            return UnaryOp(op="!", operand=self.unary())
        if self.check(TokenType.MINUS):
            self.advance()
            return UnaryOp(op="-", operand=self.unary())
        return self.primary()

    def primary(self) -> ASTNode:
        tok = self.current()

        if tok.type == TokenType.INTEGER:
            self.advance()
            return Literal(value=tok.value, kind="int")

        if tok.type == TokenType.FLOAT:
            self.advance()
            return Literal(value=tok.value, kind="float")

        if tok.type == TokenType.STRING:
            self.advance()
            return Literal(value=tok.value, kind="string")

        if tok.type == TokenType.BOOLEAN:
            self.advance()
            return Literal(value=tok.value, kind="bool")

        if tok.type == TokenType.IDENTIFIER:
            # Function call?
            if self.peek().type == TokenType.LPAREN:
                return self.call()
            self.advance()
            return Identifier(name=tok.value)

        if tok.type == TokenType.LPAREN:
            self.advance()
            expr = self.expression()
            self.expect(TokenType.RPAREN)
            return expr

        raise ParseError(
            f"Unexpected token {tok.type.name} ({tok.value!r}) at {tok.line}:{tok.column}"
        )

    def call(self) -> FunctionCall:
        name = self.advance().value  # IDENT
        self.expect(TokenType.LPAREN)
        args = []
        if not self.check(TokenType.RPAREN):
            args.append(self.expression())
            while self.match(TokenType.COMMA):
                args.append(self.expression())
        self.expect(TokenType.RPAREN)
        return FunctionCall(name=name, args=args)


# ─────────────────────────────────────────────
#  AST PRETTY PRINTER (visitor)
# ─────────────────────────────────────────────

class ASTPrinter:
    def __init__(self):
        self._indent = 0

    def _pad(self):
        return "  " * self._indent

    def generic_visit(self, node: ASTNode):
        print(f"{self._pad()}<{type(node).__name__}>")

    def visit_Program(self, node: Program):
        print(f"{self._pad()}Program")
        self._indent += 1
        for s in node.statements:
            s.accept(self)
        self._indent -= 1

    def visit_VarDeclaration(self, node: VarDeclaration):
        print(f"{self._pad()}VarDecl: {node.name}")
        self._indent += 1
        node.value.accept(self)
        self._indent -= 1

    def visit_Assignment(self, node: Assignment):
        print(f"{self._pad()}Assign: {node.name}")
        self._indent += 1
        node.value.accept(self)
        self._indent -= 1

    def visit_FunctionDeclaration(self, node: FunctionDeclaration):
        params = ", ".join(node.params)
        print(f"{self._pad()}FuncDecl: {node.name}({params})")
        self._indent += 1
        node.body.accept(self)
        self._indent -= 1

    def visit_ReturnStatement(self, node: ReturnStatement):
        print(f"{self._pad()}Return")
        if node.value:
            self._indent += 1
            node.value.accept(self)
            self._indent -= 1

    def visit_IfStatement(self, node: IfStatement):
        print(f"{self._pad()}If")
        self._indent += 1
        print(f"{self._pad()}[condition]")
        self._indent += 1
        node.condition.accept(self)
        self._indent -= 1
        print(f"{self._pad()}[then]")
        self._indent += 1
        node.then_branch.accept(self)
        self._indent -= 1
        if node.else_branch:
            print(f"{self._pad()}[else]")
            self._indent += 1
            node.else_branch.accept(self)
            self._indent -= 1
        self._indent -= 1

    def visit_WhileStatement(self, node: WhileStatement):
        print(f"{self._pad()}While")
        self._indent += 1
        print(f"{self._pad()}[condition]")
        self._indent += 1
        node.condition.accept(self)
        self._indent -= 1
        print(f"{self._pad()}[body]")
        self._indent += 1
        node.body.accept(self)
        self._indent -= 1
        self._indent -= 1

    def visit_PrintStatement(self, node: PrintStatement):
        print(f"{self._pad()}Print")
        self._indent += 1
        node.value.accept(self)
        self._indent -= 1

    def visit_Block(self, node: Block):
        print(f"{self._pad()}Block")
        self._indent += 1
        for s in node.statements:
            s.accept(self)
        self._indent -= 1

    def visit_BinaryOp(self, node: BinaryOp):
        print(f"{self._pad()}BinaryOp: {node.op!r}")
        self._indent += 1
        node.left.accept(self)
        node.right.accept(self)
        self._indent -= 1

    def visit_UnaryOp(self, node: UnaryOp):
        print(f"{self._pad()}UnaryOp: {node.op!r}")
        self._indent += 1
        node.operand.accept(self)
        self._indent -= 1

    def visit_FunctionCall(self, node: FunctionCall):
        print(f"{self._pad()}Call: {node.name}")
        self._indent += 1
        for a in node.args:
            a.accept(self)
        self._indent -= 1

    def visit_Identifier(self, node: Identifier):
        print(f"{self._pad()}Identifier: {node.name}")

    def visit_Literal(self, node: Literal):
        print(f"{self._pad()}Literal({node.kind}): {node.value!r}")


# ─────────────────────────────────────────────
#  DEMO
# ─────────────────────────────────────────────

SAMPLE = """
// Compute the factorial of a number
func factorial(n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

let x = 5;
let result = factorial(x);
print(result);

// Simple counter loop
let i = 0;
while (i < 3) {
    print(i);
    i = i + 1;
}

// Boolean and string usage
let flag = true;
let greeting = "hello";
if (flag) {
    print(greeting);
}
"""


def run(source: str, verbose_tokens: bool = True):
    print("=" * 60)
    print("SOURCE")
    print("=" * 60)
    print(source.strip())

    # ── Lexing ────────────────────────────────
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    if verbose_tokens:
        print("\n" + "=" * 60)
        print("TOKENS")
        print("=" * 60)
        for tok in tokens:
            if tok.type != TokenType.EOF:
                print(f"  {tok}")

    # ── Parsing ───────────────────────────────
    parser = Parser(tokens)
    ast = parser.parse()

    print("\n" + "=" * 60)
    print("ABSTRACT SYNTAX TREE")
    print("=" * 60)
    printer = ASTPrinter()
    ast.accept(printer)

    print("\n✓ Parsing completed successfully.\n")


if __name__ == "__main__":
    run(SAMPLE)