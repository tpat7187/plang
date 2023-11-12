from __future__ import annotations
from typing import Optional, Union, List 
from lexer import TokenType

'''
i think the way this is gonna work: 
consuming tokens pops tokens from the front of the token_stream 
peaking tokens check the next token without popping it from the stream 
'''

class Parser: 
    def __init__(self, token_stream): 
        self.token_stream = token_stream
        self.cursor = 0 

    def expect(self, tokenType:TokenType) -> bool: 
        if self.token_stream[0].type == tokenType: 
            print(f"popped {self.token_stream[0].type}")
            self.token_stream.pop(0)
        else: 
            print(f"expected token of type {tokenType} got {self.token_stream[0].type}")

    def parse_function(self) -> None:
        self.expect(TokenType.TOKENTYPE_TYPE)
        self.expect(TokenType.TOKENTYPE_IDENTIFIER)
        self.expect(TokenType.TOKENTYPE_OPENPAREN)
        # TODO: list arguments
        self.expect(TokenType.TOKENTYPE_CLOSEPAREN)
        self.expect(TokenType.TOKENTYPE_OPENCURL)
        self.parse_block()
        self.expect(TokenType.TOKENTYPE_CLOSECURL)
        self.expect(TokenType.TOKENTYPE_EOF)

    def peek_token_type(self): 
        return self.token_stream[0].type

    def parse_block(self) -> None: 
        while self.peek_token_type() != TokenType.TOKENTYPE_CLOSECURL: 
            self.parse_statement()

    def parse_statement(self): 
        self.expect(TokenType.TOKENTYPE_KEYWORD)
        self.expect(TokenType.TOKENTYPE_NUMBER)
        self.expect(TokenType.TOKENTYPE_EOL)

    def parse_tokens(self): 
        self.parse_function()


'''
program -> function 
function -> list of statements
statements -> return statement
'''
