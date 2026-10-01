"""Same-origin educational execution facade. User code never becomes host code."""
from .runtime.common import Budget, RunError, validate_source, result
from .runtime.c_vm import run_c
from .runtime.riscv import run_assembly, run_machine
from .runtime.rust_vm import run_rust
from .runtime.verilog_vm import run_verilog
from .runtime.boot_vm import run_boot

ENGINES={'c':run_c,'assembly':run_assembly,'machine':run_machine,'rust':run_rust,'verilog':run_verilog,'boot':run_boot}

def execute(code,language='c'):
    try:
        validate_source(code)
        if language not in ENGINES:raise RunError('Unknown execution language.')
        return ENGINES[language](code)
    except (RunError,RecursionError,ValueError,TypeError,KeyError,IndexError,OverflowError,AttributeError,ZeroDivisionError,SyntaxError) as e:
        return result(Budget(),language,errors=[str(e) if isinstance(e,RunError) else 'Program could not be interpreted: '+str(e)[:400]])
    except Exception as e:
        # pycparser exposes ParseError across versions; avoid leaking a server stack.
        from pycparser.c_parser import ParseError
        if isinstance(e,ParseError):return result(Budget(),language,errors=['Syntax error: '+str(e)[:400]])
        raise

# Backwards-compatible imports used by the original project.
def analyze_c_code(code):return execute(code,'c')
def analyze_assembly_code(code):return execute(code,'assembly')
