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
        self.parse_fn_arguments() # parses function arguments
        self.expect(TokenType.TOKENTYPE_CLOSEPAREN)
        self.expect(TokenType.TOKENTYPE_OPENCURL)
        self.parse_block()
        self.expect(TokenType.TOKENTYPE_CLOSECURL)
        self.expect(TokenType.TOKENTYPE_EOF)

    def parse_fn_arguments(self): 
        if self.peek_token_type() != TokenType.TOKENTYPE_CLOSEPAREN:
            self.expect(TokenType.TOKENTYPE_TYPE)
            self.expect(TokenType.TOKENTYPE_IDENTIFIER)
            while self.peek_token_type() != TokenType.TOKENTYPE_CLOSEPAREN:
                self.expect(TokenType.TOKENTYPE_COMMA)
                self.expect(TokenType.TOKENTYPE_TYPE)
                self.expect(TokenType.TOKENTYPE_IDENTIFIER)

    def peek_token_type(self): 
        return self.token_stream[0].type

    # each block ends with a CLOSECURL
    def parse_block(self) -> None: 
        while self.peek_token_type() != TokenType.TOKENTYPE_CLOSECURL: 
            self.parse_statement()

    # each statement ends with an EOL
    def parse_statement(self): 
        self.expect(TokenType.TOKENTYPE_KEYWORD)
        self.expect(TokenType.TOKENTYPE_NUMBER)
        self.expect(TokenType.TOKENTYPE_EOL)

    def parse_tokens(self): 
        self.parse_program()

    # ends program ends with an EOF
    def parse_program(self): 
        self.parse_function()

# root of program
class ProgramNode: 
    def __init__(self, function): 
        self.function = function

class FunctionNode: 
    def __init__(self, fn_type, identifier, args, statements):
        self.type = fn_type 
        self.identifier = identifier 
        self.args = args 
        self.statements = statements

class StatementNode: 
    def __init__(self, keyword, value): 
        self.keyword = keyword 
        self.value = value


'''
program -> function 
function -> list of statements (block)
statements -> return statement
'''
