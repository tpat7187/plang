from __future__ import annotations
from typing import Optional, Union, List 
from lexer import TokenType
from helpers import get_llvmtype
import llvmlite.ir as ir 
import llvmlite.binding as llvm
import os

DEBUG = os.getenv("DEBUG")

'''
i think the way this is gonna work: 
consuming tokens pops tokens from the front of the token_stream 
peaking tokens check the next token without popping it from the stream 
'''

class Parser: 
    def __init__(self, token_stream): 
        self.token_stream = token_stream
        self.cursor = 0 

    def expect(self, tokenType) -> None: 
        if not isinstance(tokenType, list): tokenType = [tokenType]
        _tok = self.token_stream[0]
        if _tok.type in tokenType: 
            if DEBUG:
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
            if DEBUG:
                print(f"popped {self.token_stream[0].type}")
            self.token_stream.pop(0)

    def parse_function(self) -> None:
        fn_type = self.expect(TokenType.TYPE)
        fn_id = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.OPENPAREN)
        args = self.parse_fn_arguments() # parses function arguments
        self.expect(TokenType.CLOSEPAREN)
        self.expect(TokenType.OPENCURL)
        statements = self.parse_block()
        self.expect(TokenType.CLOSECURL)
        return FunctionNode(fn_type, fn_id, statements, args)

    def parse_fn_arguments(self): 
        args = []
        while self.peek_token_type() != TokenType.CLOSEPAREN:
            _typ = self.expect(TokenType.TYPE)
            _id = self.expect(TokenType.IDENTIFIER)
            args.append((_typ, _id))
            self.accept(TokenType.COMMA)
        return args

    def peek_token_type(self): 
        return self.token_stream[0].type

    # each block ends with a CLOSECURL
    def parse_block(self) -> None: 
        statements = []
        while self.peek_token_type() != TokenType.CLOSECURL: 
            statements.append(self.parse_statement())
        return statements

    # each statement ends with an EOL
    def parse_statement(self): 
        if self.peek_token_type() == TokenType.KEYWORD:
            _kw = self.expect(TokenType.KEYWORD)
            expr = self.parse_expression()
            self.expect(TokenType.EOL)
            return ReturnStatementNode(_kw, expr)

        if self.peek_token_type() == TokenType.TYPE:
            _type = self.expect(TokenType.TYPE)
            _id = self.expect(TokenType.IDENTIFIER)
            self.expect(TokenType.ASSIGN)
            expr = self.parse_expression()
            self.expect(TokenType.EOL)
            return AssignStatementNode(_type, _id, expr)

    def parse_expression(self): 
        val = self.expect([TokenType.NUMBER, TokenType.IDENTIFIER])
        return ExpressionNode(val)

    # ends program ends with an EOF
    def parse_program(self): 
        fn = self.parse_function()
        self.expect(TokenType.EOF)
        return ProgramNode(fn)

    def parse_tokens(self): 
        _ast = self.parse_program()
        return _ast


# TODO: for all nodes they need a codegen method, this will call into LLVMlite
# root of program
class ProgramNode: 
    def __init__(self, function): 
        self.function = function

    # should instantiate the LLVM program
    def codegen(self): 
        mod = ir.Module(name = __file__)
        self.function.codegen(mod)
        return mod

class FunctionNode: 
    def __init__(self, fn_type, identifier, statements, args=None):
        self.type = fn_type 
        self.identifier = identifier 
        self.statements = statements
        self.args = args 

    def codegen(self, mod): 
        # return type, input types
        arg_types = [get_llvmtype(j[0].buffer) for j in self.args]
        fn_t = ir.FunctionType(get_llvmtype(self.type.buffer), arg_types)
        fn = ir.Function(mod, fn_t, name=self.identifier.buffer)
        block = fn.append_basic_block(name = 'entry') # can we not use these
        builder = ir.IRBuilder(block)
        for statement in self.statements: 
            statement.codegen(mod, builder)

class ReturnStatementNode: 
    def __init__(self, keyword, value): 
        self.keyword = keyword 
        self.value = value

    # when this gets called, it needs to codegen its children
    def codegen(self, mod, builder): 
        expr_instr = self.value.codegen(mod, builder)
        builder.ret(expr_instr)

class AssignStatementNode:
    def __init__(self, _type, _id, _value):
        self.type = _type
        self.id = _id 
        self.value = _value

    # TYPE ID ASSIGN EXPR
    # alloca the register of name id 
    # push value into that register
    def codegen(self, mod, builder): 
        llvm_type = get_llvmtype(self.type.buffer)
        expr = self.value.codegen(mod, builder)

# should this return something? sometimes we need to reference that node in the statement
class ExpressionNode: 
    def __init__(self, value, _type=None): 
        self.tok = value
        self.token_val = value.buffer
        self.type = _type 

    def codegen(self, mod, builder):
        # stores the number and returns the register
        if self.tok.type == TokenType.NUMBER:
            if self.type is None:
                alloca_instr = builder.alloca(ir.IntType(32))
            else:
                alloca_instr = builder.alloca(get_llvmtype(self.type))
            builder.store(ir.Constant(ir.IntType(32), self.token_val), alloca_instr)
            alloca_instr.align = 4
            return alloca_instr

        # return the register where the identifier is stored (?) 
        if self.tok.type == TokenType.IDENTIFIER:
            print("NOT IMPLEMENTED YET")



'''
program -> function 
function -> list of statements (block)
statements -> return statement EOL | assignment EOL | expression EOL
    return statement -> TOKEN_KEYWORD expression
    assign statement -> TYPE IDENTIFIER ASSIGN expression
expression -> Identifier | Number
'''
