"""Assembler + emulator for a bounded RV32I subset. Instructions are real encodings."""
import re
from .common import Budget, RunError, result

ALIASES={'zero':0,'ra':1,'sp':2,'gp':3,'tp':4,'t0':5,'t1':6,'t2':7,'s0':8,'fp':8,'s1':9,
         **{f'a{i}':10+i for i in range(8)},**{f's{i}':16+i for i in range(2,12)},**{f't{i}':25+i for i in range(3,7)}}

def reg(s):
    s=s.strip().lower()
    if s in ALIASES:return ALIASES[s]
    if re.fullmatch(r'x(?:[0-9]|[12][0-9]|3[01])',s):return int(s[1:])
    raise RunError(f'Unknown RV32I register: {s}')

def sx(v,bits):return v-(1<<bits) if v&(1<<(bits-1)) else v

def imm(s,labels=None):
    if labels and s in labels:return labels[s]
    try:return int(s,0) if not s.isdigit() else int(s)
    except ValueError:raise RunError(f'Invalid immediate or unknown label: {s}')

def bounded(v,bits):
    if not -(1<<(bits-1))<=v<(1<<(bits-1)):raise RunError(f'Immediate {v} does not fit a signed {bits}-bit field.')
    return v&((1<<bits)-1)

def encode(op,args,pc=0,labels=None):
    labels=labels or {}
    rtype={'add':(0,0),'sub':(0,32),'sll':(1,0),'slt':(2,0),'sltu':(3,0),'xor':(4,0),'srl':(5,0),'sra':(5,32),'or':(6,0),'and':(7,0)}
    itype={'addi':0,'slti':2,'sltiu':3,'xori':4,'ori':6,'andi':7}
    if op in rtype:
        rd,rs1,rs2=map(reg,args);f3,f7=rtype[op];return f7<<25|rs2<<20|rs1<<15|f3<<12|rd<<7|0x33
    if op in itype:
        rd,rs1=map(reg,args[:2]);v=bounded(imm(args[2],labels),12);return v<<20|rs1<<15|itype[op]<<12|rd<<7|0x13
    if op in ('slli','srli','srai'):
        rd,rs1=map(reg,args[:2]);v=imm(args[2],labels)
        if not 0<=v<32:raise RunError('Shift count must be 0–31.')
        return ((v|(0x400 if op=='srai' else 0))<<20)|rs1<<15|({'slli':1,'srli':5,'srai':5}[op])<<12|rd<<7|0x13
    if op in ('lui','auipc'):
        rd=reg(args[0]);v=imm(args[1],labels)
        if not 0<=v<1<<20:raise RunError('Upper immediate is a 20-bit unsigned field.')
        return v<<12|rd<<7|(0x37 if op=='lui' else 0x17)
    if op in ('lb','lh','lw','lbu','lhu','sb','sh','sw','jalr'):
        m=re.fullmatch(r'(.+)\(([^)]+)\)',args[1])
        if not m:raise RunError('Use offset(register), for example 4(sp).')
        rs1=reg(m[2]);v=bounded(imm(m[1],labels),12);rd=reg(args[0])
        if op.startswith('s'):
            return (v>>5)<<25|rd<<20|rs1<<15|{'sb':0,'sh':1,'sw':2}[op]<<12|(v&31)<<7|0x23
        return v<<20|rs1<<15|({'lb':0,'lh':1,'lw':2,'lbu':4,'lhu':5,'jalr':0}[op])<<12|rd<<7|(0x67 if op=='jalr' else 3)
    if op in ('beq','bne','blt','bge','bltu','bgeu'):
        rs1=reg(args[0]);rs2=reg(args[1]);v=imm(args[2],labels)-(pc if args[2] in labels else 0)
        if v%4:raise RunError('Branch target must be 4-byte aligned.')
        v=bounded(v,13);return ((v>>12)&1)<<31|((v>>5)&63)<<25|rs2<<20|rs1<<15|{'beq':0,'bne':1,'blt':4,'bge':5,'bltu':6,'bgeu':7}[op]<<12|((v>>1)&15)<<8|((v>>11)&1)<<7|0x63
    if op=='jal':
        rd=reg(args[0]);v=imm(args[1],labels)-(pc if args[1] in labels else 0)
        if v%4:raise RunError('Jump target must be 4-byte aligned.')
        v=bounded(v,21);return ((v>>20)&1)<<31|((v>>1)&1023)<<21|((v>>11)&1)<<20|((v>>12)&255)<<12|rd<<7|0x6f
    if op in ('ecall','ebreak') and not args:return 0x73 if op=='ecall' else 0x100073
    raise RunError(f'Unsupported instruction or operands: {op} {", ".join(args)}')

def expand(op,args):
    if op=='nop':return [('addi',['x0','x0','0'])]
    if op=='mv':return [('addi',[args[0],args[1],'0'])]
    if op=='j':return [('jal',['x0',args[0]])]
    if op=='ret':return [('jalr',['x0','0(ra)'])]
    if op=='call':return [('jal',['ra',args[0]])]
    if op=='beqz':return [('beq',[args[0],'zero',args[1]])]
    if op=='bnez':return [('bne',[args[0],'zero',args[1]])]
    if op=='li':
        v=imm(args[1])
        if not -(1<<31)<=v<1<<32:raise RunError('li value must fit 32 bits.')
        if -2048<=v<2048:return [('addi',[args[0],'x0',str(v)])]
        upper=((v+0x800)>>12)&0xfffff;lower=sx(v&0xfff,12)
        return [('lui',[args[0],str(upper)]),('addi',[args[0],args[0],str(lower)])]
    return [(op,args)]

def assemble(code):
    labels={};ops=[];data={};pc=0;dp=0x2000;section='text'
    for line_no,line in enumerate(code.splitlines(),1):
        line=re.split(r'#|//|;',line,1)[0].strip()
        if not line:continue
        if line in ('.text','.data'):section=line[1:];continue
        if line.startswith(('.global ','.globl ')):continue
        if ':' in line:
            label,line=line.split(':',1);label=label.strip();line=line.strip()
            if not re.fullmatch(r'[A-Za-z_]\w*',label) or label in labels:raise RunError(f'Invalid or duplicate label at line {line_no}.')
            labels[label]=pc if section=='text' else dp
            if not line:continue
        if section=='data':
            if line.startswith('.word '):
                for s in line[6:].split(','):
                    v=imm(s.strip())&0xffffffff
                    for b in v.to_bytes(4,'little'):data[dp]=b;dp+=1
            elif line.startswith('.byte '):
                for s in line[6:].split(','):data[dp]=imm(s.strip())&255;dp+=1
            else:raise RunError('Data directives support .word and .byte. Text output uses character ecall 11.')
            if dp>0x3000:raise RunError('Data limit is 4 KB.')
            continue
        pieces=line.split(None,1);op=pieces[0].lower();args=[x.strip() for x in pieces[1].split(',')] if len(pieces)>1 else []
        if op=='la':
            # Labels resolve in pass two, but pseudo instruction always occupies eight bytes.
            ops.extend([(pc,'la-hi',[args[0],args[1]],line_no),(pc+4,'la-lo',[args[0],args[1]],line_no)]);pc+=8
        else:
            for actual,a in expand(op,args):ops.append((pc,actual,a,line_no));pc+=4
        if pc>8192:raise RunError('Instruction image limit is 8 KB.')
    words=[];listing=[]
    for address,op,args,line_no in ops:
        if op.startswith('la-'):
            target=imm(args[1],labels)
            if op=='la-hi':op='lui';args=[args[0],str(((target+0x800)>>12)&0xfffff)]
            else:op='addi';args=[args[0],args[0],str(sx(target&0xfff,12))]
        try:w=encode(op,args,address,labels)
        except (IndexError,ValueError):raise RunError(f'Invalid operands at line {line_no}.')
        words.append(w);listing.append({'pc':address,'hex':f'{w:08x}','assembly':op+' '+', '.join(args),'line':line_no})
    return words,data,listing

def parse_words(code):
    words=[]
    for line in code.splitlines():
        line=re.split(r'#|//|;',line,1)[0].strip()
        for s in line.replace(',',' ').split():
            s=s.replace('_','')
            if re.fullmatch(r'[01]{32}',s):v=int(s,2)
            elif re.fullmatch(r'(?:0x)?[0-9a-fA-F]{8}',s):v=int(s,16)
            else:raise RunError('Enter 8 hex digits or 32 binary digits per RV32I instruction word. These are words, not a byte stream.')
            words.append(v)
    if len(words)>2048:raise RunError('Instruction image limit is 8 KB.')
    return words

class RVVM:
    def __init__(self):
        self.b=Budget();self.regs=[0]*32;self.regs[2]=0xe000;self.memory=bytearray(65536);self.mmio={};self.pc=0;self.halted=False
    def address(self,a,size):
        if not 0<=a<=65536-size:raise RunError(f'Memory address 0x{a:08x} is outside virtual RAM.')
        if a%size:raise RunError('Misaligned memory access.')
    def read(self,a,size,signed=False):
        self.address(a,size)
        if 0xf000<=a<0xf100:
            if size!=4:raise RunError('Virtual MMIO registers require word accesses.')
            return self.mmio.get(a,0)
        return int.from_bytes(self.memory[a:a+size],'little',signed=signed)&0xffffffff
    def write(self,a,size,v):
        self.address(a,size)
        if 0xf000<=a<0xf100:
            if size!=4:raise RunError('Virtual MMIO registers require word accesses.')
            self.mmio[a]=v&0xffffffff
        else:self.memory[a:a+size]=(v&((1<<(size*8))-1)).to_bytes(size,'little')
    def run(self,words,data=None,listing=None):
        for i,w in enumerate(words):self.memory[i*4:i*4+4]=w.to_bytes(4,'little')
        for addr,v in (data or {}).items():self.memory[addr]=v
        while not self.halted:
            if self.pc==len(words)*4:break
            if self.pc%4 or not 0<=self.pc<len(words)*4:raise RunError('Program counter escaped the instruction image.')
            old=self.pc;w=self.read(old,4);op=w&127;rd=(w>>7)&31;f3=(w>>12)&7;rs1=(w>>15)&31;rs2=(w>>20)&31;f7=w>>25
            a=self.regs[rs1];b=self.regs[rs2];next_pc=old+4;value=None;detail=''
            self.b.tick()
            if op==0x37:value=w&0xfffff000;detail='lui'
            elif op==0x17:value=(old+(w&0xfffff000));detail='auipc'
            elif op in (0x13,0x33):
                rhs=sx(w>>20,12) if op==0x13 else b;detail='alu'
                if f3==0:
                    if op==0x33 and f7 not in (0,32):raise RunError('Unsupported RV extension.')
                    value=a-rhs if op==0x33 and f7==32 else a+rhs
                elif f3==1:
                    if f7!=0:raise RunError('Invalid shift encoding.')
                    value=a<<(rhs&31)
                elif f3==2:value=int(sx(a,32)<(rhs if op==0x13 else sx(b,32)))
                elif f3==3:value=int(a<(rhs&0xffffffff))
                elif f3==4:value=a^rhs
                elif f3==5:
                    if f7 not in (0,32):raise RunError('Invalid shift encoding.')
                    value=(sx(a,32) if f7==32 else a)>>(rhs&31)
                elif f3==6:value=a|rhs
                elif f3==7:value=a&rhs
                if op==0x33 and f7 not in (0,32):raise RunError('Only RV32I integer instructions are supported.')
                if op==0x33 and f7==32 and f3 not in (0,5):raise RunError('Invalid R-type encoding.')
            elif op==3:
                if f3 not in (0,1,2,4,5):raise RunError('Unsupported load encoding.')
                addr=(a+sx(w>>20,12))&0xffffffff;size={0:1,1:2,2:4,4:1,5:2}[f3];value=self.read(addr,size,f3<4);detail=f'load 0x{addr:04x}'
            elif op==0x23:
                if f3 not in (0,1,2):raise RunError('Unsupported store encoding.')
                offset=sx((w>>25)<<5|((w>>7)&31),12);addr=(a+offset)&0xffffffff;self.write(addr,1<<f3,b);detail=f'store 0x{addr:04x} = {b}'
            elif op==0x63:
                offset=sx(((w>>31)&1)<<12|((w>>7)&1)<<11|((w>>25)&63)<<5|((w>>8)&15)<<1,13)
                cond={0:a==b,1:a!=b,4:sx(a,32)<sx(b,32),5:sx(a,32)>=sx(b,32),6:a<b,7:a>=b}
                if f3 not in cond:raise RunError('Unsupported branch encoding.')
                if cond[f3]:next_pc=old+offset
                detail='branch taken' if cond[f3] else 'branch not taken'
            elif op==0x6f:
                offset=sx(((w>>31)&1)<<20|((w>>12)&255)<<12|((w>>20)&1)<<11|((w>>21)&1023)<<1,21)
                value=old+4;next_pc=old+offset;detail='jal'
            elif op==0x67 and f3==0:value=old+4;next_pc=(a+sx(w>>20,12))&0xfffffffe;detail='jalr'
            elif w in (0x73,0x100073):
                detail='ecall'
                service=self.regs[17]
                if w==0x100073 or service in (0,10):self.halted=True
                elif service==1:self.b.emit(str(sx(self.regs[10],32)))
                elif service==11:self.b.emit(chr(self.regs[10]&255))
                elif service==4:
                    addr=self.regs[10]
                    for _ in range(4096):
                        self.b.tick();v=self.read(addr,1);addr+=1
                        if v==0:break
                        self.b.emit(chr(v))
                    else:raise RunError('String output must terminate within 4 KB.')
                else:raise RunError(f'Unknown teaching ecall {service}. Use 1=integer, 4=string, 11=character, 10=halt.')
            else:raise RunError(f'Unsupported instruction 0x{w:08x} at PC 0x{old:04x}.')
            if value is not None and rd:self.regs[rd]=value&0xffffffff
            self.regs[0]=0;self.pc=next_pc
            if len(self.b.trace)<200:self.b.trace.append({'pc':f'0x{old:04x}','word':f'{w:08x}','operation':detail,'write':f'x{rd} = {self.regs[rd]}' if value is not None and rd else '—'})
        state={'registers':{f'x{i}':v for i,v in enumerate(self.regs)},'pc':self.pc,'mmio':{str(k):v for k,v in self.mmio.items()},
               'memory':[{'address':f'0x{i:04x}','hex':self.memory[i:i+16].hex(' ')} for i in range(0x2000,0x2080,16)]}
        return result(self.b,'RV32I / instruction emulator',state,listing=listing or [],image_hex=''.join(w.to_bytes(4,'little').hex() for w in words))

def run_assembly(code):
    words,data,listing=assemble(code);return RVVM().run(words,data,listing)
def run_machine(code):return RVVM().run(parse_words(code))
