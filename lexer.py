from __future__ import annotations
from typing import Optional, Union, List, Tuple
from enum import Enum, auto

class TokenType(Enum): 
    EOF = 1,
    EOL = 2,
    OPENCURL = 3,
    CLOSECURL = 4,
    TYPE = 5,
    KEYWORD = 6,
    IDENTIFIER = 7,
    OPENPAREN = 8,
    CLOSEPAREN = 9,
    NUMBER = 10,
    OPERATOR = 11, # operators: +, -, *, /,
    COMMA = 12,
    ASSIGN = 13,
    UNKNOWN = 999

class OpsType(Enum): ADD = auto(); SUB = auto(); MUL = auto(); DIV = auto();

class Token: 
    __slots__ = "type", "buffer", "pos"
    def __init__(self, pos:Union[Tuple, int], tokenType:TokenType, buffer:Optional[List]=None):
        self.type = tokenType
        self.buffer = buffer
        self.pos = pos

    def __repr__(self): 
        return f"<{self.type}> at: [{self.pos}] with buffer: {self.buffer}"

symbol_to_tok = { 
     '{' : TokenType.OPENCURL,
     '}' : TokenType.CLOSECURL,
     '(' : TokenType.OPENPAREN,
     ')' : TokenType.CLOSEPAREN,
     ';' : TokenType.EOL,
     '=' : TokenType.ASSIGN,
     ',' : TokenType.COMMA
 }

symbol_to_op = { 
    '+' : OpsType.ADD, 
    '-' : OpsType.SUB, 
    '*' : OpsType.MUL, 
    '/' : OpsType.DIV
}



class Lexer:
    def __init__(self, input_file: string): 
        self.input_file = input_file
        self.cursor = 0
        self.token_stream = []
        self.valid_types = {'int', 'char', 'double', 'float'}
        self.valid_keywords = {'return'}
        self.valid_operators = {'+', '-', '*', '/'}

    def add_token(self, token): 
        self.token_stream.append(token)

    def lex_input_file(self): 
        _lexed = None
        while True: 
            self.generate_next_token()
            # if the most recent token is an EOF we stop generating tokens
            if self.token_stream[-1].type == TokenType.EOF:
                return self.token_stream
        

    def generate_next_token(self): 
        stream_length, content = len(self.input_file), self.input_file
        if self.cursor < stream_length-1:

            while content[self.cursor].isspace() and self.cursor < stream_length-1:
                self.cursor+=1

            if content[self.cursor] in list(symbol_to_tok.keys()): 
                _tok =  Token(self.cursor, symbol_to_tok[content[self.cursor]], None)
                self.cursor+=1
                self.add_token(_tok)

            if content[self.cursor] in self.valid_operators: 
                _tok = Token(self.cursor, TokenType.OPERATOR, symbol_to_op[content[self.cursor]])
                self.cursor+=1 
                self.add_token(_tok)

            # identifiers
            elif content[self.cursor].isalpha():
                s = self.cursor
                while content[self.cursor].isalnum(): 
                    self.cursor += 1
                _buf = content[s:self.cursor]

                if _buf in self.valid_types: 
                    _tok = Token(self.cursor, TokenType.TYPE, _buf)
                elif _buf in self.valid_keywords: 
                    _tok = Token(self.cursor, TokenType.KEYWORD, _buf)
                else:
                    _tok =  Token(self.cursor, TokenType.IDENTIFIER, _buf)
                self.add_token(_tok)

            elif content[self.cursor].isdigit():
                fp = False
                s = self.cursor
                while content[self.cursor].isdigit() or content[self.cursor] == '.':
                    if content[self.cursor] == '.': fp = True
                    self.cursor += 1

                _buf = int(content[s:self.cursor]) if fp == False else float(content[s:self.cursor])
                _tok = Token(self.cursor, TokenType.NUMBER, _buf)
                self.add_token(_tok)
        else: 
            if self.token_stream[-1].type == TokenType.EOF: 
                return None
            else: 
                _tok = Token(self.cursor, TokenType.EOF, None)
                self.add_token(_tok)










