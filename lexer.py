from __future__ import annotations
from typing import Optional, Union, List, Tuple
from enum import Enum

class TokenType(Enum): 
    TOKENTYPE_EOF = 1,
    TOKENTYPE_EOL = 2,
    TOKENTYPE_OPENCURL = 3,
    TOKENTYPE_CLOSECURL = 4,
    TOKENTYPE_TYPE = 5,
    TOKENTYPE_KEYWORD = 6,
    TOKENTYPE_IDENTIFIER = 7,
    TOKENTYPE_OPENPAREN = 8,
    TOKENTYPE_CLOSEPAREN = 9,
    TOKENTYPE_NUMBER = 10,
    TOKENTYPE_OPERATOR = 11, # operators: +, -, *, /, ','
    TOKENTYPE_COMMA = 12,
    TOKENTYPE_UNKNOWN = 999


class Token: 
    __slots__ = "type", "buffer", "pos"
    def __init__(self, pos:Union[Tuple, int], tokenType:TokenType, buffer:Optional[List]=None):
        self.type = tokenType
        self.buffer = buffer
        self.pos = pos

    def __repr__(self): 
        return f"<{self.type}> at: [{self.pos}] with buffer: {self.buffer}"

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
            if self.token_stream[-1].type == TokenType.TOKENTYPE_EOF:
                return self.token_stream
        

    def generate_next_token(self): 
        stream_length, content = len(self.input_file), self.input_file
        if self.cursor < stream_length-1:

            while content[self.cursor].isspace(): 
                self.cursor+=1

            if content[self.cursor] == ";": 
                _tok =  Token(self.cursor, TokenType.TOKENTYPE_EOL, None)
                self.cursor+=1
                self.add_token(_tok)

            elif content[self.cursor] == ",": 
                _tok = Token(self.cursor, TokenType.TOKENTYPE_COMMA, None)
                self.cursor+=1
                self.add_token(_tok)

            elif content[self.cursor] == "(": 
                _tok =  Token(self.cursor, TokenType.TOKENTYPE_OPENPAREN, None)
                self.cursor+=1
                self.add_token(_tok)

            elif content[self.cursor] == ")": 
                _tok = Token(self.cursor, TokenType.TOKENTYPE_CLOSEPAREN, None)
                self.cursor+=1
                self.add_token(_tok)

            elif content[self.cursor] == "{": 
                _tok = Token(self.cursor, TokenType.TOKENTYPE_OPENCURL, None)
                self.cursor+=1
                self.add_token(_tok)

            elif content[self.cursor] == "}": 
                _tok = Token(self.cursor, TokenType.TOKENTYPE_CLOSECURL, None)
                self.cursor+=1
                self.add_token(_tok)

            elif content[self.cursor] in self.valid_operators: 
                _tok = Token(self.cursor, TokenType.TOKENTYPE_OPERATOR, content[self.cursor]) 
                self.cursor+=1 
                self.add_token(_tok)

            # identifiers
            elif content[self.cursor].isalpha():
                s = self.cursor
                while content[self.cursor].isalnum(): 
                    self.cursor += 1
                _buf = content[s:self.cursor]

                if _buf in self.valid_types: 
                    _tok = Token(self.cursor, TokenType.TOKENTYPE_TYPE, _buf)
                elif _buf in self.valid_keywords: 
                    _tok = Token(self.cursor, TokenType.TOKENTYPE_KEYWORD, _buf)
                else:
                    _tok =  Token(self.cursor, TokenType.TOKENTYPE_IDENTIFIER, _buf)
                self.add_token(_tok)

            elif content[self.cursor].isdigit():
                fp = False
                s = self.cursor
                while content[self.cursor].isdigit() or content[self.cursor] == '.':
                    if content[self.cursor] == '.': fp = True
                    self.cursor += 1

                _buf = int(content[s:self.cursor]) if fp == False else float(content[s:self.cursor])
                _tok = Token(self.cursor, TokenType.TOKENTYPE_NUMBER, _buf)
                self.add_token(_tok)

        else: 
            if self.token_stream[-1].type == TokenType.TOKENTYPE_EOF: return None
            else: 
                _tok = Token(self.cursor, TokenType.TOKENTYPE_EOF, None)
                self.add_token(_tok)










