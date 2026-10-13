"""Small escaping-first renderer; authored Markdown cannot inject HTML/script."""
import re
from functools import lru_cache
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
register=template.Library()

def inline(s):
    s=str(escape(s))
    def token(match):
        if match[1] is not None:return '<code>'+match[1]+'</code>'
        if match[2] is not None:return '<strong>'+match[2]+'</strong>'
        label,url=match[3],match[4]
        if url.startswith('https://') or (url.startswith('/') and not url.startswith('//')):
            return '<a href="'+url+'">'+label+'</a>'
        return label
    return re.sub(r'`([^`]+)`|\*\*([^*]+)\*\*|\[([^\]]+)\]\(([^\s)]+)\)',token,s)

@register.filter
def prose(value):
    return render_prose(str(value))

# Full text is the key, so edits become visible without an invalidation job.
# Never cache an authenticated page or a learner's source here.
@lru_cache(maxsize=128)
def render_prose(value):
    lines=value.splitlines();out=[];paragraph=[];fence=False;code=[];list_kind=None;table=[];run_engine=''
    def flush():
        if paragraph:out.append('<p>'+inline(' '.join(paragraph))+'</p>');paragraph.clear()
    def endlist():
        nonlocal list_kind
        if list_kind:out.append('</'+list_kind+'>');list_kind=None
    def endtable():
        if table:
            out.append('<div class="table-scroll"><table>')
            for i,row in enumerate(table):
                tag='th' if i==0 else 'td';out.append('<tr>'+''.join('<'+tag+'>'+inline(c.strip())+'</'+tag+'>' for c in row)+'</tr>')
            out.append('</table></div>');table.clear()
    for line in lines:
        if line.startswith('```'):
            flush();endlist();endtable()
            if fence:
                block='<pre><code>'+str(escape('\n'.join(code)))+'</code></pre>'
                if run_engine:
                    block='<div class="code-example"><div class="example-tools"><span>'+str(escape(run_engine))+'</span><button type="button" class="text-button" data-load-example data-engine="'+run_engine+'">Load in terminal</button></div>'+block+'</div>'
                out.append(block);code=[];run_engine=''
            else:
                match=re.fullmatch(r'```(c|assembly|machine|rust|verilog|boot) run:[a-z0-9-]+',line)
                if match:run_engine=match[1]
            fence=not fence;continue
        if fence:code.append(line);continue
        if line.startswith('|'):
            flush();endlist()
            if not re.fullmatch(r'[|:\-\s]+',line):table.append(line.strip('|').split('|'))
            continue
        endtable()
        h=re.match(r'^(#{1,4})\s+(.+)',line)
        item=re.match(r'^(-|\d+\.)\s+(.+)',line)
        if h:flush();endlist();level=len(h[1])+1;out.append(f'<h{level}>'+inline(h[2])+f'</h{level}>')
        elif item:
            flush();kind='ul' if item[1]=='-' else 'ol'
            if list_kind!=kind:endlist();out.append('<'+kind+'>');list_kind=kind
            out.append('<li>'+inline(item[2])+'</li>')
        elif not line.strip():flush();endlist()
        elif line.startswith('> '):flush();endlist();out.append('<blockquote>'+inline(line[2:])+'</blockquote>')
        else:endlist();paragraph.append(line)
    flush();endlist();endtable()
    if fence:out.append('<pre><code>'+str(escape('\n'.join(code)))+'</code></pre>')
    return mark_safe(''.join(out))
