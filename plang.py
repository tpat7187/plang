from lexer import Lexer
from parser import Parser
import os
import sys


def read_file_from_shell(): 
    try:
        content = open(sys.argv[1], 'r').read()
    except: 
        print("ERROR: INPUT FILE DOES NOT EXIST")
    return content


def main():
  file_content = read_file_from_shell()
  flags = sys.argv[2::]

  '''
      -emit-llvm : will generate the .ll file with the same name as the input file
  '''

  #lexing
  lex = Lexer(file_content)
  token_stream = lex.lex_input_file()

  # parsing
  parser = Parser(token_stream)
  _ast = parser.parse_tokens()

  # codegen
  ir = _ast.codegen()
  print(ir)

  # for testing LLVM IR 
  if "-emit-llvm" in flags:
    llvmfile = open(f"{sys.argv[1].replace('.c', '.ll')}", "w")
    llvmfile.write(str(ir))
    llvmfile.close()

if __name__ == "__main__":
  main()

