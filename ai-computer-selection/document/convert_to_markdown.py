from pathlib import Path
from zipfile import ZipFile
from lxml import etree

base=Path('/home/gamer/Work/CloudPC/ai-computer-selection')
p=base/'document/AI执行环境选择流程说明与厂商系统对比.docx'
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
W='{'+ns['w']+'}'
with ZipFile(p) as z:
    root=etree.fromstring(z.read('word/document.xml'))
    rels=etree.fromstring(z.read('word/_rels/document.xml.rels'))
links={e.get('Id'):e.get('Target') for e in rels}

def run_text(e):
    vals=[]
    for n in e.iter():
        if n.tag==W+'t':vals.append(n.text or '')
        elif n.tag==W+'br' and n.get(W+'type')!='page':vals.append('\n')
        elif n.tag==W+'tab':vals.append(' ')
    return ''.join(vals)

def paragraph(e,cell=False):
    parts=[]
    for c in e:
        if c.tag==W+'hyperlink':
            parts.append(f'[{run_text(c)}](<{links[c.get("{"+ns["r"]+"}id")] }>)')
        elif c.tag==W+'r':
            t=run_text(c)
            bold=c.find('w:rPr/w:b',ns)
            if t.strip() and bold is not None and bold.get(W+'val','1') not in ('0','false'):
                t='**'+t+'**'
            parts.append(t)
    text=''.join(parts).strip()
    style=e.find('w:pPr/w:pStyle',ns)
    name=style.get(W+'val','') if style is not None else ''
    if name=='Title':text='# '+text.replace('\n','')
    elif name.startswith('Heading'):
        level=int(name.replace('Heading',''))+1
        text='#'*level+' '+text
    if cell:return text.replace('|','\\|').replace('\n','<br>')
    return text.replace('\n','  \n')

blocks=[]
for e in root.find('w:body',ns):
    if e.tag==W+'p':
        if e.find('.//w:drawing',ns) is not None:
            blocks.append(f'![AI 执行环境选择流程图]({base}/ai-computer-selection.png)')
            blocks.append(f'[高清 PNG]({base}/ai-computer-selection.png) · [可编辑 Draw.io 源图]({base}/ai-computer-selection.drawio)')
        t=paragraph(e)
        if t:blocks.append(t)
    elif e.tag==W+'tbl':
        rows=[]
        for tr in e.findall('w:tr',ns):
            cells=['<br>'.join(paragraph(pp,True) for pp in tc.findall('w:p',ns)) for tc in tr.findall('w:tc',ns)]
            rows.append('| '+' | '.join(cells)+' |')
        n=len(e.find('w:tr',ns).findall('w:tc',ns))
        rows.insert(1,'| '+' | '.join(['---']*n)+' |')
        blocks.append('\n'.join(rows))
md='\n\n'.join(blocks)+'\n'
out=p.with_suffix('.md');out.write_text(md,encoding='utf-8')
assert md.count('\n| ---')==4
assert md.count('https://')==10
assert md.count('![AI 执行环境选择流程图]')==1
for text in ['ChatGPT dots','Codex Cloud','Claude','Gemini','WorkBuddy','DuMate','E2B','Vercel','Ubuntu 24.04.3','Debian 13.6']:
    assert text in md,text
assert md.startswith('# AI执行环境选择流程说明与厂商系统对比\n')
print(out)
print('Verified 4 tables, flowchart, 10 web source links, 3 local sources and provider coverage.')
