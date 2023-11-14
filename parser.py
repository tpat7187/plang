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
        self.symbol_table = {}

    def codegen(self, mod): 
        # return type, input types
        arg_types = [get_llvmtype(j[0].buffer) for j in self.args]
        fn_t = ir.FunctionType(get_llvmtype(self.type.buffer), arg_types)
        fn = ir.Function(mod, fn_t, name=self.identifier.buffer)
        block = fn.append_basic_block(name = 'entry') # can we not use these
        builder = ir.IRBuilder(block)
        for statement in self.statements: 
            statement.codegen(mod, builder, self.symbol_table)

class ReturnStatementNode: 
    def __init__(self, keyword, value): 
        self.keyword = keyword 
        self.value = value

    # when this gets called, it needs to codegen its children
    def codegen(self, mod, builder, symbol_table): 
        expr_instr = self.value.codegen(mod, builder, symbol_table)
        builder.ret(expr_instr)

# TYPE ID ASSIGN EXPR
class AssignStatementNode:
    def __init__(self, _type, _id, _value):
        self.type = _type
        self.id = _id 
        self.value = _value

    def codegen(self, mod, builder, symbol_table): 
        # if the identifier is not in the symbol table we allocate memory for it
        if self.id.buffer not in symbol_table: 
            llvm_type = get_llvmtype(self.type.buffer)
            alloca_instr = builder.alloca(llvm_type)
            alloca_instr.align = 4
            symbol_table[self.id.buffer] = alloca_instr

        # evaluate expression
        expr = self.value.codegen(mod, builder, symbol_table)
        builder.store(expr, symbol_table[self.id.buffer])

class ExpressionNode: 
    def __init__(self, value, _type=None): 
        self.tok = value
        self.token_val = value.buffer
        self.type = _type 

    # expressions can either be int literals or identifiers 
    # example: 'x', 5
    def codegen(self, mod, builder, symbol_table):
        # if its a int literal we return a constant
        if self.tok.type == TokenType.NUMBER:
            if self.type is None:
                return ir.Constant(ir.IntType(32), self.token_val)
            else: 
                return ir.Constant(get_llvmtype(self.type), self.token_val)

        # if its an identifier we return the register to where that identifier is stored
        if self.tok.type == TokenType.IDENTIFIER:
            return symbol_table[self.tok.buffer]

# contains a map from identifer to register name

'''
program -> function 
function -> list of statements (block)
statements -> return statement EOL | assignment EOL | expression EOL
    return statement -> TOKEN_KEYWORD expression
    assign statement -> TYPE IDENTIFIER ASSIGN expression
expression -> Identifier | Number
'''
