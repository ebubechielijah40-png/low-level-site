"""Rust teaching subset: typed integers, bindings, loops, functions, explicit borrows.
Parses tokens into C AST dialect; never invokes a shell or Python eval.
"""
import ast
import re
from .common import RunError
from .c_vm import run_c

TOK=re.compile(r'\s+|//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\d+(?:u32|i32)?|[A-Za-z_]\w*|->|\.\.=|\.\.|==|!=|<=|>=|&&|\|\||<<|>>|\+=|-=|\*=|/=|[{}()\[\];,:!&*+\-/%<>=|^~]',re.S)

class RustParser:
    def __init__(self,code):
        self.tokens=[];pos=0
        for m in TOK.finditer(code):
            if m.start()!=pos:raise RunError(f'Unsupported Rust syntax near {code[pos:pos+20]!r}.')
            pos=m.end();s=m[0]
            if not s.isspace() and not s.startswith(('//','/*')):self.tokens.append(s)
        if pos!=len(code):raise RunError('Unsupported characters in Rust source.')
        self.i=0;self.scopes=[{}];self.functions=set()
    def peek(self):return self.tokens[self.i] if self.i<len(self.tokens) else ''
    def take(self,s=None):
        v=self.peek()
        if not v or s is not None and v!=s:raise RunError(f'Expected {s or "token"}; found {v or "end of source"}.')
        self.i+=1;return v
    def binding(self,name):
        for scope in reversed(self.scopes):
            if name in scope:return scope[name]
        return None
    def ctype(self,s):
        if s=='u32':return 'unsigned int'
        if s in ('i32','usize','bool'):return 'int'
        raise RunError(f'Type {s} is outside the Rust teaching subset (i32/u32/usize/bool).')
    def collect(self,stops):
        xs=[];depth=0
        while self.peek():
            v=self.peek()
            if depth==0 and v in stops:break
            if v in ('(','['):depth+=1
            if v in (')',']'):
                if depth==0:break
                depth-=1
            xs.append(self.take())
        if not xs:raise RunError('Expected an expression.')
        return xs
    def expr(self,xs,new_binding=None):
        result=[];borrow=None;i=0
        while i<len(xs):
            s=xs[i]
            if s=='&' and i+1<len(xs):
                mutable=xs[i+1]=='mut';j=i+2 if mutable else i+1
                if j>=len(xs):raise RunError('Borrow requires a binding.')
                name=xs[j];b=self.binding(name)
                if not b:raise RunError('Borrow a named binding declared in this scope.')
                active=[loan for scope in self.scopes for loan in scope.values() if loan.get('borrow') and loan['borrow'][0]==name]
                if mutable and not b['mutable']:raise RunError(f'{name} is immutable; use let mut before a mutable borrow.')
                if (mutable and active) or any(loan['borrow'][1] for loan in active):raise RunError('Aliasing violation: one mutable borrow or shared borrows, never both.')
                borrow=(name,mutable);result.extend(['&',name]);i=j+1;continue
            if re.fullmatch(r'[A-Za-z_]\w*',s) and self.binding(s):
                if any(v.get('borrow') and v['borrow'][0]==s and v['borrow'][1] for scope in self.scopes for v in scope.values()):
                    raise RunError(f'{s} cannot be read directly while mutably borrowed in this scope.')
            if re.fullmatch(r'\d+u32',s):s=s[:-3]+'U'
            elif re.fullmatch(r'\d+i32',s):s=s[:-3]
            elif s=='true':s='1'
            elif s=='false':s='0'
            result.append(s);i+=1
        if new_binding is not None:new_binding['borrow']=borrow
        return ' '.join(result)
    def check_write(self,xs):
        assignments={'=','+=','-=','*=','/='}
        if not any(s in assignments for s in xs):return
        if xs[0]=='*' and len(xs)>1:
            b=self.binding(xs[1])
            if not b or not b.get('borrow') or not b['borrow'][1]:raise RunError('Writing through a reference requires &mut.')
            return
        b=self.binding(xs[0])
        if b:
            if not b['mutable']:raise RunError(f'{xs[0]} is immutable. Declare it with let mut.')
            if any(v.get('borrow') and v['borrow'][0]==xs[0] for s in self.scopes for v in s.values()):raise RunError(f'{xs[0]} cannot be written while borrowed in this scope.')
    def block(self):
        self.take('{');self.scopes.append({});out=['{']
        while self.peek()!='}':
            if not self.peek():raise RunError('Unclosed Rust block.')
            out.append(self.stmt())
        self.take('}');self.scopes.pop();out.append('}');return '\n'.join(out)
    def stmt(self):
        s=self.peek()
        if s=='let':
            self.take();mutable=False
            if self.peek()=='mut':self.take();mutable=True
            name=self.take()
            if not re.fullmatch(r'[A-Za-z_]\w*',name):raise RunError('Invalid binding name.')
            typ='int'
            if self.peek()==':':
                self.take();typ=self.ctype(self.take())
            self.take('=');xs=self.collect({';'});self.take(';')
            b={'mutable':mutable,'borrow':None};ex=self.expr(xs,b)
            if b['borrow']:typ+='*'
            if xs and xs[0]=='[':
                if xs[-1]!=']' or ';' in xs:raise RunError('Use an explicit array initializer [1, 2, 3].')
                count=xs.count(',')+1;decl=f'{typ} {name}[{count}] = '+'{'+self.expr(xs[1:-1])+'};'
            else:decl=f'{typ} {name} = {ex};'
            self.scopes[-1][name]=b;return decl
        if s in ('while','if'):
            self.take();xs=self.collect({'{'});out=s+' ('+self.expr(xs)+') '+self.block()
            if s=='if' and self.peek()=='else':self.take();out+=' else '+(self.stmt() if self.peek()=='if' else self.block())
            return out
        if s=='for':
            self.take();name=self.take();self.take('in');start=self.collect({'..','..='});inclusive=self.take()=='..=';end=self.collect({'{'})
            self.scopes.append({name:{'mutable':False,'borrow':None}})
            body=self.block();self.scopes.pop()
            return f'for(int {name}={self.expr(start)}; {name}{"<=" if inclusive else "<"}{self.expr(end)}; {name}++) '+body
        if s in ('break','continue'):
            self.take();self.take(';');return s+';'
        if s=='return':
            self.take();xs=self.collect({';'});self.take(';');return 'return '+self.expr(xs)+';'
        if s=='println':
            self.take();self.take('!');self.take('(');fmt=self.take()
            if not fmt.startswith('"'):raise RunError('println! requires a literal format string.')
            fmt=ast.literal_eval(fmt);parts=[]
            while self.peek()==',':self.take();parts.append(self.expr(self.collect({',',')'})))
            self.take(')');self.take(';')
            if fmt.count('{}')!=len(parts):raise RunError('println! {} count does not match arguments.')
            if '%' in fmt:fmt=fmt.replace('%','%%')
            fmt=fmt.replace('{}','%d')+'\n'
            escaped='"'+fmt.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')+'"'
            return 'printf('+escaped+(','+','.join(parts) if parts else '')+');'
        if s=='{':return self.block()
        xs=self.collect({';','}'})
        if self.peek()==';':
            self.take();self.check_write(xs);return self.expr(xs)+';'
        return 'return '+self.expr(xs)+';'
    def parse(self):
        out=[]
        while self.peek():
            self.take('fn');name=self.take();self.take('(');params=[];scope={}
            while self.peek()!=')':
                param=self.take();self.take(':');typ=self.ctype(self.take());params.append(typ+' '+param);scope[param]={'mutable':False,'borrow':None}
                if self.peek()!=',':break
                self.take()
            self.take(')');typ='int'
            if self.peek()=='->':self.take();typ=self.ctype(self.take())
            self.scopes.append(scope);body=self.block();self.scopes.pop();out.append(typ+' '+name+'('+(','.join(params) if params else 'void')+') '+body)
        return '\n'.join(out)

def run_rust(code):
    generated=RustParser(code).parse();r=run_c(generated);r['engine']='Rust / teaching subset with borrow checks';return r
