"""Bounded C AST interpreter. A documented ILP32 teaching dialect, not a C compiler."""
import ast
import re
from dataclasses import dataclass
from pycparser import c_parser, c_ast
from .common import Budget, RunError, result

UNINITIALISED = object()

class Return(Exception):
    def __init__(self, value=0): self.value=value
class Break(Exception): pass
class Continue(Exception): pass

class Number(int):
    def __new__(cls, value, unsigned=False):
        obj=int.__new__(cls, value); obj.unsigned=unsigned; return obj

def number(v, unsigned=False):
    v=int(v)
    if unsigned: return Number(v & 0xffffffff, True)
    if v < -2147483648 or v > 2147483647:
        raise RunError('Signed 32-bit overflow. C does not define wrapping signed overflow; use an unsigned type.')
    return Number(v)

@dataclass
class Cell:
    value: object = 0
    type: str = 'int'
    alive: bool = True

@dataclass
class Pointer:
    cells: list
    index: int = 0
    def cell(self):
        if self.index < 0 or self.index >= len(self.cells): raise RunError('Invalid pointer or out-of-bounds access.')
        cell=self.cells[self.index]
        if not cell.alive:raise RunError('Pointer refers to an object whose lifetime has ended.')
        return cell

class CVM:
    def __init__(self):
        self.b=Budget(); self.scopes=[{}]; self.functions={}; self.mmio={}; self.depth=0
        self.structs={}; self.final={};self.allocated=0
    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope: return scope[name]
        raise RunError(f'Unknown variable: {name}')
    def typename(self, t):
        if isinstance(t, c_ast.TypeDecl): return self.typename(t.type)
        if isinstance(t, c_ast.IdentifierType): return ' '.join(t.names)
        if isinstance(t, c_ast.PtrDecl): return self.typename(t.type)+'*'
        if isinstance(t, c_ast.ArrayDecl): return self.typename(t.type)+'[]'
        if isinstance(t, c_ast.Struct):
            if t.decls: self.structs[t.name]=t.decls
            return 'struct '+str(t.name)
        return 'int'
    def convert(self,v,t):
        if t.endswith('*') and isinstance(v,list): return Pointer(v)
        if isinstance(v,(Pointer,list,dict,str)): return v
        if t.endswith('*'):
            raise RunError('Raw host pointers are unavailable. Use &variable or mmio_read/mmio_write for virtual devices.')
        if t.startswith('struct'): return v
        if 'float' in t or 'double' in t: raise RunError('Floating point is outside this C teaching dialect.')
        if 'char' in t:
            v=int(v)&255; return Number(v if 'unsigned' in t or v<128 else v-256)
        if 'short' in t:
            v=int(v)&65535; return Number(v if 'unsigned' in t or v<32768 else v-65536)
        if 'unsigned' in t: return Number(int(v)&0xffffffff,True)
        return number(v)
    def ref(self,n):
        if isinstance(n,c_ast.ID): return self.lookup(n.name)
        if isinstance(n,c_ast.UnaryOp) and n.op=='*':
            p=self.expr(n.expr)
            if not isinstance(p,Pointer): raise RunError('Dereferencing a value which is not a pointer.')
            return p.cell()
        if isinstance(n,c_ast.ArrayRef):
            a=self.expr(n.name); i=int(self.expr(n.subscript))
            if isinstance(a,Pointer): return Pointer(a.cells,a.index+i).cell()
            if not isinstance(a,list) or not 0<=i<len(a): raise RunError('Array index is out of bounds.')
            return a[i]
        if isinstance(n,c_ast.StructRef):
            obj=self.expr(n.name)
            if n.type=='->': obj=obj.cell().value if isinstance(obj,Pointer) else None
            if not isinstance(obj,dict) or n.field.name not in obj:raise RunError('Unknown structure field.')
            return obj[n.field.name]
        raise RunError('Expression is not assignable in this dialect.')
    def binary(self,op,a,b):
        if isinstance(a,Pointer) and op in ('+','-'):return Pointer(a.cells,a.index+(int(b) if op=='+' else -int(b)))
        unsigned=getattr(a,'unsigned',False) or getattr(b,'unsigned',False)
        if unsigned: a=int(a)&0xffffffff;b=int(b)&0xffffffff
        if op in ('/','%') and b==0:raise RunError('Division by zero.')
        if op in ('<<','>>') and not 0<=b<32:raise RunError('Shift count must be between 0 and 31.')
        if op=='+':v=a+b
        elif op=='-':v=a-b
        elif op=='*':v=a*b
        elif op=='/':v=(abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1)
        elif op=='%':v=a-self.binary('/',a,b)*b
        elif op=='&':v=a&b
        elif op=='|':v=a|b
        elif op=='^':v=a^b
        elif op=='<<':v=a<<b
        elif op=='>>':v=a>>b
        elif op=='==':return Number(int(a==b))
        elif op=='!=':return Number(int(a!=b))
        elif op=='<':return Number(int(a<b))
        elif op=='<=':return Number(int(a<=b))
        elif op=='>':return Number(int(a>b))
        elif op=='>=':return Number(int(a>=b))
        else:raise RunError(f'Unsupported operator: {op}')
        return number(v,unsigned)
    def expr(self,n):
        self.b.tick()
        if n is None:return Number(0)
        if isinstance(n,c_ast.Constant):
            if n.type=='string':return ast.literal_eval(n.value)
            if n.type=='char':return Number(ord(ast.literal_eval(n.value)))
            raw=re.sub(r'[uUlL]+$','',n.value); base=16 if raw.lower().startswith('0x') else 8 if len(raw)>1 and raw[0]=='0' else 10
            return number(int(raw,base),'u' in n.value.lower() or int(raw,base)>2147483647)
        if isinstance(n,c_ast.ID):
            v=self.lookup(n.name).value
            if v is UNINITIALISED:raise RunError(f'Read of uninitialised variable: {n.name}')
            return v
        if isinstance(n,(c_ast.ArrayRef,c_ast.StructRef)):
            v=self.ref(n).value
            if v is UNINITIALISED:raise RunError('Read of an uninitialised element or field.')
            return v
        if isinstance(n,c_ast.BinaryOp):
            a=self.expr(n.left)
            if n.op=='&&':return Number(int(bool(a) and bool(self.expr(n.right))))
            if n.op=='||':return Number(int(bool(a) or bool(self.expr(n.right))))
            return self.binary(n.op,a,self.expr(n.right))
        if isinstance(n,c_ast.UnaryOp):
            if n.op=='&':
                if isinstance(n.expr,c_ast.ArrayRef):
                    array=self.expr(n.expr.name);index=int(self.expr(n.expr.subscript))
                    if isinstance(array,Pointer):return Pointer(array.cells,array.index+index)
                    if isinstance(array,list):return Pointer(array,index)
                return Pointer([self.ref(n.expr)])
            if n.op=='sizeof':
                if isinstance(n.expr,c_ast.Typename):t=self.typename(n.expr.type)
                elif isinstance(n.expr,c_ast.ID):
                    cell=self.lookup(n.expr.name);t=cell.type
                    if isinstance(cell.value,list):return Number(len(cell.value)*self.size(t.replace('[]','')))
                else:t='int'
                return Number(self.size(t))
            if n.op in ('p++','p--','++','--'):
                cell=self.ref(n.expr);old=cell.value;cell.value=self.convert(self.binary('+' if '+' in n.op else '-',old,1),cell.type)
                return old if n.op.startswith('p') else cell.value
            v=self.expr(n.expr)
            if n.op=='*':
                if not isinstance(v,Pointer):raise RunError('Dereferencing a non-pointer.')
                out=v.cell().value
                if out is UNINITIALISED:raise RunError('Read through a pointer to an uninitialised object.')
                return out
            if n.op=='!':return Number(int(not v))
            if n.op=='~':return number(~v,getattr(v,'unsigned',False))
            if n.op=='-':return number(-v,getattr(v,'unsigned',False))
            if n.op=='+':return v
            raise RunError(f'Unsupported unary operator: {n.op}')
        if isinstance(n,c_ast.Cast):return self.convert(self.expr(n.expr),self.typename(n.to_type.type))
        if isinstance(n,c_ast.TernaryOp):return self.expr(n.iftrue if self.expr(n.cond) else n.iffalse)
        if isinstance(n,c_ast.Assignment):
            cell=self.ref(n.lvalue);v=self.expr(n.rvalue)
            if n.op!='=':v=self.binary(n.op[:-1],cell.value,v)
            cell.value=self.convert(v,cell.type);return cell.value
        if isinstance(n,c_ast.FuncCall):
            if not isinstance(n.name,c_ast.ID):raise RunError('Indirect function calls are outside this dialect.')
            args=[self.expr(a) for a in (n.args.exprs if n.args else [])]
            return self.call(n.name.name,args)
        if isinstance(n,c_ast.ExprList):
            value=0
            for e in n.exprs:value=self.expr(e)
            return value
        if isinstance(n,c_ast.InitList):return [Cell(self.expr(e)) for e in n.exprs]
        raise RunError(f'Unsupported C syntax: {type(n).__name__}. See Runner reference.')
    def size(self,t):
        if t.startswith('struct '):raise RunError('Native structure layout and sizeof(struct) are outside this interpreter.')
        if '*' in t:return 4
        if 'char' in t:return 1
        if 'short' in t:return 2
        return 4
    def decl(self,n):
        if n.name is None:self.typename(n.type);return
        if isinstance(n.type,c_ast.FuncDecl):return
        t=self.typename(n.type)
        self.allocated+=1
        if self.allocated>8192:raise RunError('Virtual-object allocation limit reached.')
        if isinstance(n.type,c_ast.ArrayDecl):
            size=int(self.expr(n.type.dim)) if n.type.dim else len(n.init.exprs) if isinstance(n.init,c_ast.InitList) else 0
            if size<1 or size>1024:raise RunError('Array size must be 1–1024 elements.')
            self.allocated+=size
            if self.allocated>8192:raise RunError('Virtual-object allocation limit reached.')
            values=self.expr(n.init) if n.init else []
            if not isinstance(values,list) or len(values)>size:raise RunError('Invalid array initializer.')
            v=[Cell(self.convert(x.value,t.replace('[]','')),t.replace('[]','')) for x in values]+[Cell(0 if n.init or len(self.scopes)==1 else UNINITIALISED,t.replace('[]','')) for _ in range(size-len(values))]
        elif t.startswith('struct '):
            name=t.split(' ',1)[1]; fields=self.structs.get(name)
            if not fields:raise RunError('Unknown structure type.')
            v={f.name:Cell(0 if len(self.scopes)==1 else UNINITIALISED,self.typename(f.type)) for f in fields}
            if n.init:
                vals=self.expr(n.init)
                for f,x in zip(fields,vals):v[f.name].value=self.convert(x.value,v[f.name].type)
        else:v=self.convert(self.expr(n.init),t) if n.init else 0 if len(self.scopes)==1 else UNINITIALISED
        if n.name in self.scopes[-1]:raise RunError(f'Duplicate declaration: {n.name}')
        self.scopes[-1][n.name]=Cell(v,t)
    def end_scope(self,scope):
        def invalidate(cell):
            cell.alive=False
            if isinstance(cell.value,list):
                for child in cell.value:invalidate(child)
            elif isinstance(cell.value,dict):
                for child in cell.value.values():invalidate(child)
        for cell in scope.values():invalidate(cell)
    def stmt(self,n):
        if n is None:return
        self.b.tick(f'line {n.coord.line}: {type(n).__name__}' if n.coord else None)
        if isinstance(n,c_ast.Compound):
            self.scopes.append({})
            try:
                for x in n.block_items or []:self.stmt(x)
            finally:
                self.final.update({k:self.serialize(c.value) for k,c in self.scopes[-1].items()});self.end_scope(self.scopes[-1]);self.scopes.pop()
        elif isinstance(n,c_ast.Decl):self.decl(n)
        elif isinstance(n,c_ast.DeclList):
            for d in n.decls:self.decl(d)
        elif isinstance(n,c_ast.If):self.stmt(n.iftrue if self.expr(n.cond) else n.iffalse)
        elif isinstance(n,(c_ast.While,c_ast.For,c_ast.DoWhile)):
            self.scopes.append({})
            try:
                if isinstance(n,c_ast.For):self.stmt(n.init)
                first=True
                while (first and isinstance(n,c_ast.DoWhile)) or n.cond is None or self.expr(n.cond):
                    first=False
                    try:self.stmt(n.stmt)
                    except Continue:pass
                    except Break:break
                    if isinstance(n,c_ast.For):self.expr(n.next)
            finally:self.end_scope(self.scopes[-1]);self.scopes.pop()
        elif isinstance(n,c_ast.Return):raise Return(self.expr(n.expr))
        elif isinstance(n,c_ast.Break):raise Break()
        elif isinstance(n,c_ast.Continue):raise Continue()
        elif isinstance(n,c_ast.EmptyStatement):pass
        else:self.expr(n)
    def serialize(self,v):
        if v is UNINITIALISED:return '<uninitialised>'
        if isinstance(v,list):return [self.serialize(c.value) for c in v]
        if isinstance(v,dict):return {k:self.serialize(c.value) for k,c in v.items()}
        if isinstance(v,Pointer):return {'pointer_index':v.index,'length':len(v.cells)}
        return v
    def call(self,name,args):
        self.b.tick()
        if name=='printf':
            if not args or not isinstance(args[0],str):raise RunError('printf requires a string format.')
            fmt=args[0]; vals=iter(args[1:]); chunks=[];pos=0
            for m in re.finditer(r'%(?:0?(\d{1,2}))?([duxXcsi%])',fmt):
                if '%' in fmt[pos:m.start()]:raise RunError('Unsupported printf format. Use %d, %u, %x, %c, %s, or %%.')
                chunks.append(fmt[pos:m.start()]);kind=m.group(2)
                if kind=='%':s='%'
                else:
                    try:v=next(vals)
                    except StopIteration:raise RunError('Not enough printf arguments.')
                    if kind in ('d','i'):s=str(int(v))
                    elif kind=='u':s=str(int(v)&0xffffffff)
                    elif kind in ('x','X'):s=format(int(v)&0xffffffff,kind)
                    elif kind=='c':s=chr(int(v)&255)
                    else:s=str(v)
                    if m.group(1):s=s.rjust(int(m.group(1)),'0' if fmt[m.start()+1]=='0' else ' ')
                chunks.append(s);pos=m.end()
            if '%' in fmt[pos:]:raise RunError('Unsupported printf format. Use %d, %u, %x, %c, %s, or %%.')
            chunks.append(fmt[pos:]);text=''.join(chunks)
            if re.search(r'%(?![%])',fmt) and not list(re.finditer(r'%(?:0?(\d{1,2}))?([duxXcsi%])',fmt)):raise RunError('Unsupported printf format.')
            self.b.emit(text);return Number(len(text))
        if name=='puts':self.b.emit(str(args[0])+'\n');return Number(0)
        if name=='putchar':self.b.emit(chr(int(args[0])&255));return args[0]
        if name=='mmio_write':
            if len(args)!=2 or not 0xf000<=int(args[0])<0xf100 or int(args[0])%4:raise RunError('Virtual device registers use aligned addresses 0xF000–0xF0FC.')
            self.mmio[int(args[0])]=int(args[1])&0xffffffff;return Number(0)
        if name=='mmio_read':
            if len(args)!=1 or not 0xf000<=int(args[0])<0xf100 or int(args[0])%4:raise RunError('Invalid MMIO register address.')
            return number(self.mmio.get(int(args[0]),0),True)
        if name not in self.functions:raise RunError(f'Function {name} is unavailable. No file, shell, or network functions are exposed.')
        f=self.functions[name];params=f.decl.type.args.params if f.decl.type.args else []
        params=[p for p in params if isinstance(p,c_ast.Decl)]
        if len(params)!=len(args):raise RunError(f'{name} expects {len(params)} arguments.')
        self.depth+=1
        if self.depth>40:raise RunError('Call-depth limit reached (40).')
        caller_scopes=self.scopes
        self.scopes=[caller_scopes[0],{p.name:Cell(self.convert(v,self.typename(p.type)),self.typename(p.type)) for p,v in zip(params,args)}]
        try:
            try:self.stmt(f.body)
            except Return as e:return e.value
            return Number(0)
        finally:self.end_scope(self.scopes[-1]);self.scopes=caller_scopes;self.depth-=1
    def run(self,code):
        # Accept only known headers; they are declarations, never read from the host.
        allowed={'stdio.h','stdint.h','stddef.h','stdbool.h','limits.h'}
        defs={}
        def directive(m):
            text=m.group(0)
            inc=re.fullmatch(r'#\s*include\s*[<"]([^>"]+)[>"]\s*',text)
            if inc:
                if inc[1] not in allowed:raise RunError(f'Header {inc[1]} is outside the teaching dialect.')
                return ''
            define=re.fullmatch(r'#\s*define\s+(\w+)\s+([-+]?0x[0-9a-fA-F]+|[-+]?\d+)\s*',text)
            if define:defs[define[1]]=define[2];return ''
            raise RunError('Only known #include headers and integer #define constants are supported.')
        code=re.sub(r'^\s*#[^\n]*',directive,code,flags=re.M)
        # Strip comments without changing strings or source line numbers.
        code=re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*.*?\*/|//[^\n]*',lambda m: '\n'*m[0].count('\n') if m[0].startswith(('/*','//')) else m[0],code,flags=re.S)
        code=re.sub(r'"(?:\\.|[^"\\])*"|\b[A-Za-z_]\w*\b',lambda m:m[0] if m[0].startswith('"') else defs.get(m[0],m[0]),code)
        prefix='typedef unsigned int uint32_t; typedef int int32_t; typedef unsigned char uint8_t; typedef unsigned int size_t; typedef int bool;\n'
        code=re.sub(r'\btrue\b','1',code);code=re.sub(r'\bfalse\b','0',code)
        tree=c_parser.CParser().parse(prefix+code,filename='editor.c')
        for n in tree.ext:
            if isinstance(n,c_ast.FuncDef):self.functions[n.decl.name]=n
            elif isinstance(n,c_ast.Decl):self.decl(n)
        if 'main' not in self.functions:raise RunError('Define an int main(void) entry point.')
        exit_code=int(self.call('main',[]))
        return result(self.b,'C / bounded AST interpreter',{'variables':self.final,'mmio':{str(k):v for k,v in self.mmio.items()}},exit_code=exit_code)

def run_c(code):return CVM().run(code)
