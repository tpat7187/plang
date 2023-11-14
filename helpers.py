import llvmlite.ir as ir

def get_llvmtype(typedef):
    fn_types = { 
        "int"    : ir.IntType(32),
        "float"  : ir.FloatType(),
        "void"   : ir.VoidType(),
        "double" : ir.DoubleType()
    }

    return fn_types[typedef]





