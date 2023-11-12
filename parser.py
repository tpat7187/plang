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

    def expect(self, tokenType:TokenType) -> None: 
        _tok = self.token_stream[0]
        if _tok.type == tokenType: 
            print(f"popped {self.token_stream[0].type}")
            self.token_stream.pop(0)
        else: 
            print(f"expected token of type {tokenType} got {self.token_stream[0].type}")
            exit(1)

        return _tok

    # doesnt throw an error if the token types do not match, will pop if there is one
    def accept(self, tokenType:TokenType) -> None:
        _tok = self.token_stream[0] 
        if _tok.type == tokenType: 
            print(f"popped {self.token_stream[0].type}")
            self.token_stream.pop(0)

    def parse_function(self) -> None:
        fn_type = self.expect(TokenType.TOKENTYPE_TYPE)
        fn_id = self.expect(TokenType.TOKENTYPE_IDENTIFIER)
        self.expect(TokenType.TOKENTYPE_OPENPAREN)
        args = self.parse_fn_arguments() # parses function arguments
        self.expect(TokenType.TOKENTYPE_CLOSEPAREN)
        self.expect(TokenType.TOKENTYPE_OPENCURL)
        statements = self.parse_block()
        self.expect(TokenType.TOKENTYPE_CLOSECURL)
        return FunctionNode(fn_type, fn_id, statements, args)

    def parse_fn_arguments(self): 
        args = []
        while self.peek_token_type() != TokenType.TOKENTYPE_CLOSEPAREN:
            _typ = self.expect(TokenType.TOKENTYPE_TYPE)
            _id = self.expect(TokenType.TOKENTYPE_IDENTIFIER)
            args.append((_typ, _id))
            self.accept(TokenType.TOKENTYPE_COMMA)
        return args

    def peek_token_type(self): 
        return self.token_stream[0].type

    # each block ends with a CLOSECURL
    def parse_block(self) -> None: 
        statements = []
        while self.peek_token_type() != TokenType.TOKENTYPE_CLOSECURL: 
            statements.append(self.parse_statement())
        return statements

    # each statement ends with an EOL
    def parse_statement(self): 
        kw = self.expect(TokenType.TOKENTYPE_KEYWORD)
        num = self.expect(TokenType.TOKENTYPE_NUMBER)
        self.expect(TokenType.TOKENTYPE_EOL)
        return StatementNode(kw, num)

    # ends program ends with an EOF
    def parse_program(self): 
        fn = self.parse_function()
        self.expect(TokenType.TOKENTYPE_EOF)
        return ProgramNode(fn)

    def parse_tokens(self): 
        _ast = self.parse_program()
        return _ast


# root of program
class ProgramNode: 
    def __init__(self, function): 
        self.function = function

class FunctionNode: 
    def __init__(self, fn_type, identifier, statements, args=None):
        self.type = fn_type 
        self.identifier = identifier 
        self.statements = statements
        self.args = args 

class StatementNode: 
    def __init__(self, keyword, value): 
        self.keyword = keyword 
        self.value = value


'''
program -> function 
function -> list of statements (block)
statements -> return statement
'''
