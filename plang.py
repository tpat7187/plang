from lexer import Lexer
from parser import Parser
import sys


def read_file_from_shell(): 
    try:
        content = open(sys.argv[1], 'r').read()
    except: 
        print("ERROR: INPUT FILE DOES NOT EXIST")
    return content



def main():
  file_content = read_file_from_shell()

  #lexing
  lex = Lexer(file_content)
  token_stream = lex.lex_input_file()

  # parsing
  parser = Parser(token_stream)
  _ast = parser.parse_tokens()

  #codegen
  ir = _ast.codegen()

  print(ir)






if __name__ == "__main__":
  main()

