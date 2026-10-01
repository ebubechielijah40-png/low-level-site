"""Build the editable Markdown technical report into a print-ready PDF."""
from pathlib import Path
import re
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Flowable,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

root=Path(__file__).resolve().parents[1]
output=root/'output/pdf';output.mkdir(parents=True,exist_ok=True)
font=Path('/usr/share/fonts/truetype/dejavu')
for name,file in [('ReportSans','DejaVuSans.ttf'),('ReportBold','DejaVuSans-Bold.ttf'),('ReportMono','DejaVuSansMono.ttf')]:pdfmetrics.registerFont(TTFont(name,str(font/file)))
GREEN=colors.HexColor('#244F37');PALE=colors.HexColor('#EAF1E7');INK=colors.HexColor('#22342A');MUTED=colors.HexColor('#617067');LINE=colors.HexColor('#C9D6C7')
styles={
 'body':ParagraphStyle('body',fontName='ReportSans',fontSize=9.1,leading=14,textColor=INK,spaceAfter=9),
 'h2':ParagraphStyle('h2',fontName='ReportBold',fontSize=18.5,leading=24,textColor=GREEN,spaceBefore=7,spaceAfter=15,keepWithNext=True),
 'h3':ParagraphStyle('h3',fontName='ReportBold',fontSize=11.5,leading=16,textColor=GREEN,spaceBefore=13,spaceAfter=6,keepWithNext=True),
 'cell':ParagraphStyle('cell',fontName='ReportSans',fontSize=8.2,leading=12.2,textColor=INK),
 'cellhead':ParagraphStyle('cellhead',fontName='ReportBold',fontSize=8.2,leading=12.2,textColor=GREEN),
 'code':ParagraphStyle('code',fontName='ReportMono',fontSize=8,leading=11.4,textColor=GREEN,backColor=PALE,borderPadding=9,spaceAfter=13),
 'small':ParagraphStyle('small',fontName='ReportSans',fontSize=8,leading=13,textColor=MUTED,spaceAfter=10),
}
def clean(s):
 return s.translate(str.maketrans({'–':'-','—':'-','‑':'-','→':'->','’':"'",'“':'"','”':'"'}))
def inline(s):
 s=escape(clean(s));s=re.sub(r'`([^`]+)`',r'<font name="ReportMono" color="#244F37">\1</font>',s);s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
 return s
class Cover(Flowable):
 def __init__(self):super().__init__();self.width=487;self.height=690
 def draw(self):
  c=self.canv;h=self.height
  c.setFillColor(GREEN);c.rect(0,h-25,24,24,fill=1,stroke=0);c.setFillColor(PALE)
  for x in range(3):
   for y in range(3):c.rect(5+x*5,h-20+y*5,3,3,fill=1,stroke=0)
  c.setFont('ReportMono',8);c.setFillColor(MUTED);c.drawString(38,h-16,'FINAL-YEAR PROJECT / TECHNICAL REPORT')
  c.setFont('ReportBold',49);c.setFillColor(GREEN);c.drawString(0,h-117,'Bare Metal')
  subtitle=['An integrated environment for learning','and applying low-level programming languages']
  c.setFont('ReportSans',16);c.setFillColor(INK)
  for i,line in enumerate(subtitle):c.drawString(0,h-162-i*25,line)
  c.setStrokeColor(LINE);c.setLineWidth(1);c.line(0,h-230,487,h-230)
  c.setFont('ReportMono',9);c.setFillColor(MUTED);c.drawString(0,h-256,'EXISTING REPOSITORY UPGRADE     /     01 OCTOBER 2026')
  c.setFont('ReportSans',10);c.setFillColor(INK)
  for i,line in enumerate(['Machine code. Assembly. C. Rust. Verilog. OS foundations.',
                            'Read the mechanism, run the experiment, inspect the state.']):c.drawString(0,h-303-i*20,line)
  c.setFillColor(PALE);c.rect(0,h-480,487,108,fill=1,stroke=0)
  for x,num,label in [(18,'33','AUTHORED LESSONS'),(181,'13','CONFIGURATIONS'),(345,'163','TESTS PASSED')]:
   c.setFillColor(GREEN);c.setFont('ReportMono',31);c.drawString(x,h-421,num);c.setFont('ReportMono',7);c.drawString(x,h-447,label)
  c.setFillColor(MUTED);c.setFont('ReportSans',9)
  for i,line in enumerate(['Evidence and execution contracts are included.',
                            'Browser visual checks and native-kernel boot remain unverified.',
                            'Hardware views and language subsets state their limits explicitly.']):c.drawString(0,h-535-i*18,line)
  c.setStrokeColor(GREEN);c.line(0,33,487,33);c.setFont('ReportMono',7);c.setFillColor(GREEN);c.drawString(0,16,'CL-fromgithub -> Bare Metal / SOURCE + REPORT + REPRODUCIBLE CHECKS')

def frame(c,doc):
 c.saveState();c.setFillColor(colors.HexColor('#FAFCF8'));c.rect(0,0,*A4,fill=1,stroke=0)
 if doc.page>1:
  c.setFillColor(GREEN);c.setFont('ReportMono',7);c.drawString(54,809,'BARE METAL  /  TECHNICAL PROJECT REPORT');c.setStrokeColor(LINE);c.line(54,798,541,798)
 c.setStrokeColor(LINE);c.line(54,44,541,44);c.setFillColor(MUTED);c.setFont('ReportMono',7);c.drawString(54,30,'01 OCT 2026  /  IMPLEMENTED SCOPE AND VERIFIED EVIDENCE');c.drawRightString(541,30,f'{doc.page:02d}');c.restoreState()

story=[Cover(),PageBreak()];lines=(root/'docs/PROJECT_REPORT.md').read_text().splitlines();para=[];rows=[];fence=False;code=[];section=None

def flush():
 if para:story.append(KeepTogether([Paragraph(inline(' '.join(para)),styles['body'])]));para.clear()
def flush_table():
 if not rows:return
 cols=len(rows[0]);widths=[40,165,282] if cols==3 else [126,361] if cols==2 else [487/cols]*cols
 cells=[[Paragraph(inline(s.strip()),styles['cellhead' if i==0 else 'cell']) for s in row] for i,row in enumerate(rows)]
 t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('LINEBELOW',(0,0),(-1,0),.8,LINE),('LINEBELOW',(0,1),(-1,-1),.4,LINE),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.extend([t,Spacer(1,16)]);rows.clear()
for line in lines:
 if line.startswith('# Bare Metal') or line.startswith('## Design and implementation') or line.startswith('Technical final-year project'):continue
 if line.startswith('```'):
  flush();flush_table()
  if fence:story.append(Paragraph('<br/>'.join(escape(clean(x)).replace(' ','&nbsp;') for x in code),styles['code']));code=[]
  fence=not fence;continue
 if fence:code.append(line);continue
 if line.startswith('|'):
  flush()
  if not re.fullmatch(r'[|:\-\s]+',line):rows.append(line.strip('|').split('|'))
  continue
 flush_table()
 if line.startswith('## '):
  flush();name=line[3:]
  if name not in ('Abstract','Deliverable inventory and provenance'):story.append(PageBreak())
  story.append(Paragraph(inline(name),styles['h2']));section=name
 elif line.startswith('### '):flush();story.append(Paragraph(inline(line[4:]),styles['h3']))
 elif not line.strip():flush()
 else:para.append(line)
flush();flush_table()
doc=SimpleDocTemplate(str(output/'Bare-Metal-Project-Report.pdf'),pagesize=A4,leftMargin=54,rightMargin=54,topMargin=61,bottomMargin=61,
                      title='Bare Metal - Technical final-year project report',author='Bare Metal project',subject='Implemented learning environment, architecture, verification, and limits')
doc.build(story,onFirstPage=frame,onLaterPages=frame)
print(output/'Bare-Metal-Project-Report.pdf')
