from enum import Enum, auto


class TokenType(Enum):
    # Literals
    INTEGER     = auto()
    FLOAT       = auto()
    STRING      = auto()

    # Identifiers & Keywords
    IDENTIFIER  = auto()
    CAST        = auto()   # function definition
    SUMMON      = auto()   # variable declaration
    BANISH      = auto()   # return statement
    IF_CURSED   = auto()   # if
    ELSE_WARD   = auto()   # else
    WHILE_ENCHANTED = auto()  # while loop
    TRUE_RUNE   = auto()   # boolean true
    FALSE_RUNE  = auto()   # boolean false
    INSCRIBE    = auto()   # print / output

    # Arithmetic Operators
    PLUS        = auto()
    MINUS       = auto()
    MULTIPLY    = auto()
    DIVIDE      = auto()
    MODULO      = auto()
    POWER       = auto()

    # Comparison Operators
    EQ          = auto()   # ==
    NEQ         = auto()   # !=
    LT          = auto()   # <
    GT          = auto()   # >
    LTE         = auto()   # <=
    GTE         = auto()   # >=

    # Logical Operators
    AND_BIND    = auto()   # &&
    OR_WEAVE    = auto()   # ||
    NOT_DISPEL  = auto()   # !

    # Assignment
    ASSIGN      = auto()   # =

    # Delimiters
    LPAREN      = auto()   # (
    RPAREN      = auto()   # )
    LBRACE      = auto()   # {
    RBRACE      = auto()   # }
    LBRACKET    = auto()   # [
    RBRACKET    = auto()   # ]
    COMMA       = auto()   # ,
    SEMICOLON   = auto()   # ;
    COLON       = auto()   # :
    DOT         = auto()   # .

    # Special
    COMMENT     = auto()   # ~~ ...
    NEWLINE     = auto()
    EOF         = auto()
    UNKNOWN     = auto()


# Maps keyword strings -> TokenType
KEYWORDS: dict[str, TokenType] = {
    "cast":             TokenType.CAST,
    "summon":           TokenType.SUMMON,
    "banish":           TokenType.BANISH,
    "if_cursed":        TokenType.IF_CURSED,
    "else_ward":        TokenType.ELSE_WARD,
    "while_enchanted":  TokenType.WHILE_ENCHANTED,
    "true_rune":        TokenType.TRUE_RUNE,
    "false_rune":       TokenType.FALSE_RUNE,
    "inscribe":         TokenType.INSCRIBE,
}


class Token:
    """Represents a single token produced by the lexer."""

    def __init__(self, token_type: TokenType, value: str, line: int, column: int):
        self.type   = token_type
        self.value  = value
        self.line   = line
        self.column = column

    def __repr__(self) -> str:
        return (
            f"Token(type={self.type.name:<20} "
            f"value={repr(self.value):<20} "
            f"line={self.line}, col={self.column})"
        )
