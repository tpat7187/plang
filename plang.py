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
  lex = Lexer(file_content)
  token_stream = lex.lex_input_file()
  parser = Parser(token_stream)
  parser.parse_tokens()







if __name__ == "__main__":
  main()

