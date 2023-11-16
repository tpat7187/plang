import llvmlite.ir as ir
from lexer import DType

def get_llvmtype(typedef):
  fn_types = { 
      DType.INT    : ir.IntType(32),
      DType.FLOAT  : ir.FloatType(),
      DType.VOID   : ir.VoidType(),
      DType.DOUBLE : ir.DoubleType()
  }

  return fn_types[typedef]





