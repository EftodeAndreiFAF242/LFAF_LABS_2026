"""
ArcaneScript Lexer
------------------
Performs lexical analysis on ArcaneScript source code and produces
a flat list of Token objects.

ArcaneScript syntax highlights:
    - summon x = 42;              # variable declaration
    - cast greet(name) { ... }    # function definition
    - banish result;              # return
    - if_cursed (x > 0) { ... }  # conditional
    - else_ward { ... }           # else branch
    - while_enchanted (x != 0)   # loop
    - inscribe("Hello!");         # print
    - ~~ this is a comment        # comment (to end of line)
    - true_rune / false_rune      # boolean literals
"""

from arc_token import Token, TokenType, KEYWORDS


class LexerError(Exception):
    """Raised when the lexer encounters an unrecognised character."""

    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"LexerError at line {line}, col {column}: {message}")
        self.line   = line
        self.column = column


class Lexer:
    """
    Transforms a raw ArcaneScript source string into a list of tokens.

    Usage:
        lexer  = Lexer(source_code)
        tokens = lexer.tokenize()
    """

    def __init__(self, source: str):
        self.source  = source
        self.pos     = 0          # current character index
        self.line    = 1          # 1-based line counter
        self.column  = 1          # 1-based column counter
        self.tokens: list[Token] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def tokenize(self) -> list[Token]:
        """Scan the entire source and return the token list."""
        while not self._is_at_end():
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens

    # ------------------------------------------------------------------
    # Core scanning
    # ------------------------------------------------------------------

    def _scan_token(self) -> None:
        """Identify and consume the next token starting at self.pos."""
        ch = self._current_char()

        # --- Whitespace (skip, but track newlines) ---
        if ch in (" ", "\t", "\r"):
            self._advance()
            return

        if ch == "\n":
            self._add_token(TokenType.NEWLINE, ch)
            self._advance()
            self.line  += 1
            self.column = 1
            return

        # --- Comments  ~~  ---
        if ch == "~" and self._peek() == "~":
            self._read_comment()
            return

        # --- String literals ---
        if ch in ('"', "'"):
            self._read_string(ch)
            return

        # --- Numbers ---
        if ch.isdigit():
            self._read_number()
            return

        # --- Identifiers / keywords ---
        if ch.isalpha() or ch == "_":
            self._read_identifier()
            return

        # --- Two-character operators ---
        if ch == "=" and self._peek() == "=":
            self._add_token(TokenType.EQ, "=="); self._advance(); self._advance(); return
        if ch == "!" and self._peek() == "=":
            self._add_token(TokenType.NEQ, "!="); self._advance(); self._advance(); return
        if ch == "<" and self._peek() == "=":
            self._add_token(TokenType.LTE, "<="); self._advance(); self._advance(); return
        if ch == ">" and self._peek() == "=":
            self._add_token(TokenType.GTE, ">="); self._advance(); self._advance(); return
        if ch == "&" and self._peek() == "&":
            self._add_token(TokenType.AND_BIND, "&&"); self._advance(); self._advance(); return
        if ch == "|" and self._peek() == "|":
            self._add_token(TokenType.OR_WEAVE, "||"); self._advance(); self._advance(); return
        if ch == "*" and self._peek() == "*":
            self._add_token(TokenType.POWER, "**"); self._advance(); self._advance(); return

        # --- Single-character tokens ---
        single: dict[str, TokenType] = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.MULTIPLY,
            "/": TokenType.DIVIDE,
            "%": TokenType.MODULO,
            "=": TokenType.ASSIGN,
            "<": TokenType.LT,
            ">": TokenType.GT,
            "!": TokenType.NOT_DISPEL,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            "[": TokenType.LBRACKET,
            "]": TokenType.RBRACKET,
            ",": TokenType.COMMA,
            ";": TokenType.SEMICOLON,
            ":": TokenType.COLON,
            ".": TokenType.DOT,
        }

        if ch in single:
            self._add_token(single[ch], ch)
            self._advance()
            return

        # --- Unknown character ---
        self._add_token(TokenType.UNKNOWN, ch)
        self._advance()

    # ------------------------------------------------------------------
    # Readers for complex token types
    # ------------------------------------------------------------------

    def _read_comment(self) -> None:
        """Consume  ~~ ... <EOL>  as a single COMMENT token."""
        start_col = self.column
        comment   = ""
        while not self._is_at_end() and self._current_char() != "\n":
            comment += self._current_char()
            self._advance()
        self.tokens.append(Token(TokenType.COMMENT, comment, self.line, start_col))

    def _read_string(self, quote: str) -> None:
        """Consume a quoted string literal, supporting escape sequences."""
        start_line = self.line
        start_col  = self.column
        result     = quote
        self._advance()  # opening quote

        while not self._is_at_end():
            ch = self._current_char()
            if ch == "\\":                  # escape sequence
                result += ch
                self._advance()
                if not self._is_at_end():
                    result += self._current_char()
                    self._advance()
                continue
            if ch == quote:                 # closing quote
                result += ch
                self._advance()
                break
            if ch == "\n":
                raise LexerError("Unterminated string literal", start_line, start_col)
            result += ch
            self._advance()

        self.tokens.append(Token(TokenType.STRING, result, start_line, start_col))

    def _read_number(self) -> None:
        """Consume an integer or float literal."""
        start_col  = self.column
        number_str = ""
        is_float   = False

        while not self._is_at_end() and self._current_char().isdigit():
            number_str += self._current_char()
            self._advance()

        # Decimal part
        if not self._is_at_end() and self._current_char() == "." and self._peek().isdigit():
            is_float    = True
            number_str += "."
            self._advance()
            while not self._is_at_end() and self._current_char().isdigit():
                number_str += self._current_char()
                self._advance()

        tok_type = TokenType.FLOAT if is_float else TokenType.INTEGER
        self.tokens.append(Token(tok_type, number_str, self.line, start_col))

    def _read_identifier(self) -> None:
        """Consume an identifier or keyword (including multi-word keywords like if_cursed)."""
        start_col = self.column
        ident     = ""

        while not self._is_at_end() and (self._current_char().isalnum() or self._current_char() == "_"):
            ident += self._current_char()
            self._advance()

        tok_type = KEYWORDS.get(ident, TokenType.IDENTIFIER)
        self.tokens.append(Token(tok_type, ident, self.line, start_col))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _current_char(self) -> str:
        return self.source[self.pos]

    def _peek(self) -> str:
        """Look one character ahead without consuming."""
        next_pos = self.pos + 1
        return self.source[next_pos] if next_pos < len(self.source) else "\0"

    def _advance(self) -> str:
        ch         = self.source[self.pos]
        self.pos  += 1
        self.column += 1
        return ch

    def _add_token(self, token_type: TokenType, value: str) -> None:
        self.tokens.append(Token(token_type, value, self.line, self.column))

    def _is_at_end(self) -> bool:
        return self.pos >= len(self.source)
