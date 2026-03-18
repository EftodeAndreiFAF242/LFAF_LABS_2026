"""
tests/test_lexer.py
--------------------
Unit tests for the ArcaneScript lexer.

Run:
    python -m unittest tests.test_lexer -v
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lexer import Lexer, LexerError
from arc_token import TokenType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def lex(source: str):
    tokens = Lexer(source).tokenize()
    return [t for t in tokens if t.type != TokenType.EOF]


def types(source: str):
    tokens = Lexer(source).tokenize()
    return [t.type for t in tokens if t.type not in (TokenType.NEWLINE, TokenType.EOF)]


# ---------------------------------------------------------------------------
# Literals
# ---------------------------------------------------------------------------

class TestLiterals(unittest.TestCase):

    def test_integer(self):
        toks = lex("42")
        self.assertEqual(toks[0].type,  TokenType.INTEGER)
        self.assertEqual(toks[0].value, "42")

    def test_float(self):
        toks = lex("3.14")
        self.assertEqual(toks[0].type,  TokenType.FLOAT)
        self.assertEqual(toks[0].value, "3.14")

    def test_integer_not_float(self):
        self.assertEqual(types("100"), [TokenType.INTEGER])

    def test_string_double_quote(self):
        toks = lex('"hello"')
        self.assertEqual(toks[0].type,  TokenType.STRING)
        self.assertEqual(toks[0].value, '"hello"')

    def test_string_single_quote(self):
        toks = lex("'world'")
        self.assertEqual(toks[0].type,  TokenType.STRING)
        self.assertEqual(toks[0].value, "'world'")

    def test_string_escape(self):
        toks = lex(r'"say \"hi\""')
        self.assertEqual(toks[0].type, TokenType.STRING)



# ---------------------------------------------------------------------------
# Keywords
# ---------------------------------------------------------------------------

class TestKeywords(unittest.TestCase):

    def test_all_keywords(self):
        keyword_map = {
            "cast":            TokenType.CAST,
            "summon":          TokenType.SUMMON,
            "banish":          TokenType.BANISH,
            "if_cursed":       TokenType.IF_CURSED,
            "else_ward":       TokenType.ELSE_WARD,
            "while_enchanted": TokenType.WHILE_ENCHANTED,
            "true_rune":       TokenType.TRUE_RUNE,
            "false_rune":      TokenType.FALSE_RUNE,
            "inscribe":        TokenType.INSCRIBE,
        }
        for kw, expected_type in keyword_map.items():
            with self.subTest(keyword=kw):
                self.assertEqual(types(kw), [expected_type])

    def test_identifier_not_keyword(self):
        self.assertEqual(types("myVariable"), [TokenType.IDENTIFIER])

    def test_partial_keyword_is_identifier(self):
        self.assertEqual(types("summons"), [TokenType.IDENTIFIER])


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

class TestOperators(unittest.TestCase):

    def test_arithmetic(self):
        self.assertEqual(types("+ - * / %"), [
            TokenType.PLUS, TokenType.MINUS,
            TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO,
        ])

    def test_power(self):
        self.assertEqual(types("**"), [TokenType.POWER])

    def test_comparison(self):
        self.assertEqual(types("== != < > <= >="), [
            TokenType.EQ, TokenType.NEQ,
            TokenType.LT, TokenType.GT,
            TokenType.LTE, TokenType.GTE,
        ])

    def test_logical(self):
        self.assertEqual(types("&& || !"), [
            TokenType.AND_BIND, TokenType.OR_WEAVE, TokenType.NOT_DISPEL,
        ])

    def test_assign(self):
        self.assertEqual(types("="), [TokenType.ASSIGN])


# ---------------------------------------------------------------------------
# Delimiters
# ---------------------------------------------------------------------------

class TestDelimiters(unittest.TestCase):

    def test_all_delimiters(self):
        self.assertEqual(types("( ) { } [ ] , ; : ."), [
            TokenType.LPAREN, TokenType.RPAREN,
            TokenType.LBRACE, TokenType.RBRACE,
            TokenType.LBRACKET, TokenType.RBRACKET,
            TokenType.COMMA, TokenType.SEMICOLON,
            TokenType.COLON, TokenType.DOT,
        ])


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

class TestComments(unittest.TestCase):

    def test_comment_is_single_token(self):
        toks = [t for t in lex("~~ this is a spell comment") if t.type != TokenType.NEWLINE]
        self.assertEqual(len(toks), 1)
        self.assertEqual(toks[0].type, TokenType.COMMENT)
        self.assertIn("this is a spell comment", toks[0].value)

    def test_comment_does_not_consume_next_line(self):
        result = types("~~ comment\nsummon x = 1;")
        self.assertIn(TokenType.SUMMON, result)


# ---------------------------------------------------------------------------
# Integration
# ---------------------------------------------------------------------------

class TestIntegration(unittest.TestCase):

    def test_variable_declaration(self):
        self.assertEqual(types("summon hp = 100;"), [
            TokenType.SUMMON, TokenType.IDENTIFIER,
            TokenType.ASSIGN, TokenType.INTEGER, TokenType.SEMICOLON,
        ])

    def test_function_definition_header(self):
        self.assertEqual(types("cast heal(target, amount) {"), [
            TokenType.CAST, TokenType.IDENTIFIER,
            TokenType.LPAREN, TokenType.IDENTIFIER,
            TokenType.COMMA, TokenType.IDENTIFIER,
            TokenType.RPAREN, TokenType.LBRACE,
        ])

    def test_if_statement(self):
        self.assertEqual(types("if_cursed (x >= 0) {"), [
            TokenType.IF_CURSED,
            TokenType.LPAREN, TokenType.IDENTIFIER,
            TokenType.GTE, TokenType.INTEGER,
            TokenType.RPAREN, TokenType.LBRACE,
        ])

    def test_while_loop(self):
        self.assertEqual(types("while_enchanted (n != 0) {"), [
            TokenType.WHILE_ENCHANTED,
            TokenType.LPAREN, TokenType.IDENTIFIER,
            TokenType.NEQ, TokenType.INTEGER,
            TokenType.RPAREN, TokenType.LBRACE,
        ])

    def test_inscribe_call(self):
        self.assertEqual(types('inscribe("hello");'), [
            TokenType.INSCRIBE,
            TokenType.LPAREN, TokenType.STRING,
            TokenType.RPAREN, TokenType.SEMICOLON,
        ])

    def test_power_expression(self):
        self.assertEqual(types("x ** 2"), [
            TokenType.IDENTIFIER, TokenType.POWER, TokenType.INTEGER,
        ])

    def test_line_tracking(self):
        source = "summon x = 1;\nsummon y = 2;"
        tokens = [t for t in lex(source) if t.type == TokenType.SUMMON]
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[1].line, 2)

    def test_unknown_character(self):
        toks = lex("@")
        self.assertEqual(toks[0].type, TokenType.UNKNOWN)


if __name__ == "__main__":
    unittest.main()