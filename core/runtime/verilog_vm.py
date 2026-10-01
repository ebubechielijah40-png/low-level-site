"""Bounded combinational Verilog simulator. Exhaustive truth tables, no synthesis."""
import re
from .common import Budget, RunError, result
from .c_vm import CVM
from pycparser import c_parser, c_ast

def run_verilog(code):
    b=Budget();code=re.sub(r'//[^\n]*|/\*.*?\*/','',code,flags=re.S)
    m=re.fullmatch(r'\s*module\s+(\w+)\s*\((.*?)\)\s*;(.*?)endmodule\s*',code,re.S)
    if not m:raise RunError('Use one module with ANSI input/output declarations and continuous assign statements.')
    ports=m[2];body=m[3];inputs={};outputs={};kind=None;width=1
    for p in ports.split(','):
        p=p.strip();decl=re.fullmatch(r'(?:(input|output)\s+(?:(?:wire|logic)\s+)?(?:\[(\d+):0\]\s+)?)?(\w+)',p)
        if not decl:raise RunError(f'Invalid port declaration: {p}')
        if decl[1]:kind=decl[1];width=int(decl[2])+1 if decl[2] else 1
        if kind is None or width>4:raise RunError('Declare input/output ports with widths of 1–4 bits.')
        name=decl[3]
        if name in inputs or name in outputs:raise RunError('Duplicate port name.')
        (inputs if kind=='input' else outputs)[name]=width
    if not inputs or not outputs or sum(inputs.values())>8:raise RunError('Use 1–8 total input bits and at least one output.')
    assignments=[]
    for stmt in body.split(';'):
        if not stmt.strip():continue
        a=re.fullmatch(r'\s*assign\s+(\w+)\s*=\s*(.*?)\s*',stmt,re.S)
        if not a or a[1] not in outputs:raise RunError('Only continuous assign to output ports is supported. always/posedge requires a sequential simulator.')
        expr=re.sub(r"(\d+)'([bhd])([0-9a-fA-F_]+)",lambda x:str(int(x[3].replace('_',''),{'b':2,'h':16,'d':10}[x[2]]) & ((1 << min(int(x[1]),32))-1)),a[2])
        for nm,w in {**inputs,**outputs}.items():
            expr=re.sub(r'\b'+re.escape(nm)+r'\[(\d+)\]',lambda x:f'(({nm} >> {x[1]}) & 1)' if int(x[1])<w else (_ for _ in ()).throw(RunError('Bit select is outside the signal width.')),expr)
        if any(x in expr for x in (';','{','}','#','"')):raise RunError('Unsupported Verilog expression.')
        tree=c_parser.CParser().parse('int main(void){ int value = '+expr+'; }')
        node=tree.ext[0].body.block_items[0].init
        allowed=(c_ast.BinaryOp,c_ast.UnaryOp,c_ast.Constant,c_ast.ID,c_ast.TernaryOp)
        def check(n):
            if not isinstance(n,allowed):raise RunError('Only combinational expressions are supported.')
            for _,child in n.children():check(child)
        check(node);assignments.append((a[1],node))
    if set(x[0] for x in assignments)!=set(outputs) or len(assignments)!=len(outputs):raise RunError('Each output must have exactly one continuous assignment.')
    rows=[]
    for vector in range(1<<sum(inputs.values())):
        b.tick();vm=CVM();shift=0;row={}
        from .c_vm import Cell
        for name,width in inputs.items():row[name]=(vector>>shift)&((1<<width)-1);shift+=width
        vm.scopes=[{k:Cell(v) for k,v in row.items()}]
        for name,node in assignments:
            value=int(vm.expr(node))&((1<<outputs[name])-1);row[name]=value;vm.scopes[0][name]=Cell(value)
        rows.append(row)
    b.emit(' | '.join([*inputs,*outputs])+'\n')
    for row in rows:b.emit(' | '.join(str(row[x]) for x in [*inputs,*outputs])+'\n')
    b.trace=[f'Evaluated {len(rows)} input vectors; outputs are masked to their declared width.']
    return result(b,'Verilog / combinational simulation',{'truth_table':rows,'signals':{**inputs,**outputs}},exit_code=0)
