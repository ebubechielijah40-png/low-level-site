"""Actual x86 16-bit boot-sector bytes with a deliberately small BIOS emulator."""
import ast
import re
from .common import Budget, RunError, result
R16=['ax','cx','dx','bx','sp','bp','si','di'];R8=['al','cl','dl','bl','ah','ch','dh','bh']
DEFAULT_BOOT='''bits 16
org 0x7c00
start:
    xor ax, ax
    mov ds, ax
    mov si, message
    mov ah, 0x0e
print:
    lodsb
    cmp al, 0
    je done
    int 0x10
    jmp print
done:
    hlt
message:
    db "BARE METAL OS", 13, 10, "Booted from your own 512-byte image.", 13, 10, 0
'''

def split_args(s):return [x.strip() for x in re.findall(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[^,]+',s)]
def value(s,labels):
    if s in labels:return labels[s]
    if s.startswith(('"',"'")):
        v=ast.literal_eval(s)
        if len(v)!=1:raise RunError('Instruction character literals must be one character.')
        return ord(v)
    try:return int(s,0) if not s.isdigit() else int(s)
    except ValueError:raise RunError(f'Unknown boot label or value: {s}')

def instruction(op,args,pc,labels,sizing=False):
    val=lambda s:value(s,labels) if not sizing else 0
    word=lambda v:(v&65535).to_bytes(2,'little')
    if op=='db':
        out=bytearray()
        for a in args:
            if a.startswith(('"',"'")):
                try:out.extend(ast.literal_eval(a).encode('ascii'))
                except (UnicodeEncodeError,ValueError,SyntaxError):raise RunError('Boot strings must be ASCII.')
            else:
                n=val(a)
                if not sizing and not 0<=n<=255:raise RunError('db values must fit one byte.')
                out.append(n&255)
        return bytes(out)
    if op=='mov' and len(args)==2:
        if args[0] in R16:return bytes([0xb8+R16.index(args[0])])+word(val(args[1]))
        if args[0] in R8:
            v=val(args[1])
            if not sizing and not 0<=v<=255:raise RunError('8-bit register immediate must fit one byte.')
            return bytes([0xb0+R8.index(args[0]),v&255])
        if args[0] in ('es','ss','ds') and args[1] in R16:return bytes([0x8e,0xc0|{'es':0,'ss':2,'ds':3}[args[0]]<<3|R16.index(args[1])])
    if op=='xor' and len(args)==2 and args[0] in R16 and args[1] in R16:return bytes([0x31,0xc0|R16.index(args[1])<<3|R16.index(args[0])])
    if op=='int' and len(args)==1:return bytes([0xcd,val(args[0])&255])
    if op in ('jmp','call') and len(args)==1:
        v=val(args[0])-pc-3
        if not sizing and not -32768<=v<=32767:raise RunError('Jump is out of range.')
        return bytes([0xe9 if op=='jmp' else 0xe8])+word(v)
    if op in ('je','jz','jne','jnz','loop') and len(args)==1:
        v=val(args[0])-pc-2
        if not sizing and not -128<=v<128:raise RunError('Conditional jump must fit the signed 8-bit range.')
        return bytes([{'je':0x74,'jz':0x74,'jne':0x75,'jnz':0x75,'loop':0xe2}[op],v&255])
    if op=='cmp' and len(args)==2 and args[0] in ('al','ax'):return bytes([0x3c if args[0]=='al' else 0x3d])+(bytes([val(args[1])&255]) if args[0]=='al' else word(val(args[1])))
    if op in ('push','pop','inc','dec') and len(args)==1 and args[0] in R16:return bytes([{'push':0x50,'pop':0x58,'inc':0x40,'dec':0x48}[op]+R16.index(args[0])])
    if op in ('add','sub') and len(args)==2 and args[0]=='ax':return bytes([0x05 if op=='add' else 0x2d])+word(val(args[1]))
    if not args and op in ('lodsb','hlt','cli','sti','cld','nop','ret'):return bytes([{'lodsb':0xac,'hlt':0xf4,'cli':0xfa,'sti':0xfb,'cld':0xfc,'nop':0x90,'ret':0xc3}[op]])
    raise RunError(f'Unsupported boot instruction: {op} {", ".join(args)}. This is the x86 boot teaching subset.')

def build_boot(code):
    pc=0x7c00;labels={};ops=[]
    for line in code.splitlines():
        # Preserve semicolons inside quoted strings.
        line=re.sub(r'"(?:\\.|[^"\\])*"|;[^\n]*',lambda m:'' if m[0].startswith(';') else m[0],line).strip()
        if not line:continue
        if line.lower() in ('bits 16','org 0x7c00'):continue
        if re.fullmatch(r'times\s+510\s*-\s*\(\$-\$\$\)\s+db\s+0',line,re.I) or line.lower()=='dw 0xaa55':continue
        if ':' in line and not line.startswith('db '):
            label,line=line.split(':',1);label=label.strip();line=line.strip()
            if not re.fullmatch(r'[A-Za-z_]\w*',label) or label in labels:raise RunError('Invalid or duplicate boot label.')
            labels[label]=pc
            if not line:continue
        p=line.split(None,1);op=p[0].lower();args=split_args(p[1]) if len(p)>1 else []
        length=len(instruction(op,args,pc,labels,True));ops.append((pc,op,args));pc+=length
        if pc-0x7c00>510:raise RunError('Boot program and data must fit 510 bytes; the last two bytes hold the BIOS signature.')
    image=b''.join(instruction(op,args,addr,labels) for addr,op,args in ops)
    return image.ljust(510,b'\0')+b'\x55\xaa'

class BootVM:
    def __init__(self,image):
        if len(image)!=512 or image[510:]!=b'\x55\xaa':raise RunError('A boot image must be exactly 512 bytes and end in 55 AA.')
        self.memory=bytearray(65536);self.memory[0x7c00:0x7e00]=image;self.regs=[0]*8;self.regs[4]=0x7c00;self.pc=0x7c00;self.ds=0;self.zf=False;self.b=Budget();self.image=image
    def fetch(self):
        if not 0x7c00<=self.pc<0x7e00:raise RunError('Instruction pointer left the boot sector.')
        v=self.memory[self.pc];self.pc+=1;return v
    def word(self):return self.fetch()|self.fetch()<<8
    def put8(self,r,v):
        parent=r%4;shift=8 if r>=4 else 0;self.regs[parent]=(self.regs[parent]&~(255<<shift))|((v&255)<<shift)
    def get8(self,r):return (self.regs[r%4]>>(8 if r>=4 else 0))&255
    def push(self,v):
        sp=self.regs[4]-2
        if not 0x6000<=sp<0x7c00:raise RunError('Boot stack left its virtual range.')
        self.regs[4]=sp;self.memory[sp:sp+2]=(v&65535).to_bytes(2,'little')
    def pop(self):
        sp=self.regs[4]
        if not 0x6000<=sp<0x7c00:raise RunError('Boot stack underflow.')
        self.regs[4]+=2;return int.from_bytes(self.memory[sp:sp+2],'little')
    def run(self):
        halted=False
        while not halted:
            old=self.pc;op=self.fetch();self.b.tick();name=f'opcode {op:02x}'
            if 0xb8<=op<=0xbf:self.regs[op-0xb8]=self.word();name='mov r16, immediate'
            elif 0xb0<=op<=0xb7:self.put8(op-0xb0,self.fetch());name='mov r8, immediate'
            elif op==0x31:
                m=self.fetch()
                if m<0xc0:raise RunError('Boot XOR only supports register operands.')
                a=m&7;self.regs[a]^=self.regs[(m>>3)&7];self.zf=self.regs[a]==0;name='xor'
            elif op==0x8e:
                m=self.fetch();value_=self.regs[m&7]
                if m<0xc0 or value_!=0:raise RunError('Boot teaching emulator supports only zero-valued real-mode segments.')
                self.ds=0;name='mov segment, register'
            elif op==0xac:
                self.put8(0,self.memory[self.regs[6]]);self.regs[6]=(self.regs[6]+1)&65535;name='lodsb'
            elif op in (0x3c,0x3d):self.zf=(self.get8(0) if op==0x3c else self.regs[0])==(self.fetch() if op==0x3c else self.word());name='cmp'
            elif op in (0xe9,0xe8):
                offset=self.word();offset=offset-65536 if offset>=32768 else offset
                if op==0xe8:self.push(self.pc)
                self.pc+=offset;name='jmp' if op==0xe9 else 'call'
            elif op in (0x74,0x75,0xe2):
                offset=self.fetch();offset=offset-256 if offset>=128 else offset
                if op==0xe2:self.regs[1]=(self.regs[1]-1)&65535
                if self.zf if op==0x74 else not self.zf if op==0x75 else self.regs[1]!=0:self.pc+=offset
                name='conditional jump'
            elif op==0xcd:
                interrupt=self.fetch()
                if interrupt!=0x10 or self.get8(4)!=0x0e:raise RunError('Only BIOS INT 10h / AH=0Eh teletype output is available.')
                self.b.emit(chr(self.get8(0)));name='BIOS teletype'
            elif 0x50<=op<=0x57:self.push(self.regs[op-0x50]);name='push'
            elif 0x58<=op<=0x5f:self.regs[op-0x58]=self.pop();name='pop'
            elif 0x40<=op<=0x4f:
                idx=op&7;self.regs[idx]=(self.regs[idx]+(1 if op<0x48 else -1))&65535;self.zf=self.regs[idx]==0;name='inc/dec'
            elif op in (0x05,0x2d):
                v=self.word();self.regs[0]=(self.regs[0]+(v if op==5 else -v))&65535;self.zf=self.regs[0]==0;name='add/sub'
            elif op==0xc3:self.pc=self.pop();name='ret'
            elif op==0xf4:halted=True;name='hlt'
            elif op in (0xfa,0xfb,0xfc,0x90):name='control/nop'
            else:raise RunError(f'Unsupported x86 opcode {op:02x} at {old:04x}. Only the documented boot subset is emulated.')
            if len(self.b.trace)<200:self.b.trace.append({'ip':f'{old:04x}','operation':name,'ax':f'{self.regs[0]:04x}','si':f'{self.regs[6]:04x}'})
        return result(self.b,'x86 / 16-bit boot emulator',{'registers':{r:self.regs[i] for i,r in enumerate(R16)},'ip':self.pc,'halted':halted},image_hex=self.image.hex(),screen=self.b.output.replace('\r',''))

def run_boot(code):return BootVM(build_boot(code)).run()
