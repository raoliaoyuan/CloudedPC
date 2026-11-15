from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from copy import deepcopy
import re, hashlib, json
from lxml import etree as E

BASE=Path('/home/gamer/Work/CloudPC')
OUT=BASE/'codex-dot-workbuddy-comparison-2026-11-15'
STEM='Codex Dot对比 Workbuddy云PC对比分析报告及GUI体验分析'
REF=BASE/'云PC软硬件检查报告.docx'
MD=OUT/'报告正文.md'
FINAL=OUT/(STEM+'.docx')
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def q(n): return '{'+NS['w']+'}'+n
def el(n,**attrs):
    x=E.Element(q(n))
    for k,v in attrs.items(): x.set(q(k),str(v))
    return x
with ZipFile(REF) as z: parts={n:z.read(n) for n in z.namelist()}
assert hashlib.sha256(REF.read_bytes()).hexdigest()=='fc206e63af54b37f193e7a92d31869354598059053167358798009ea561e1428'
root=E.fromstring(parts['word/document.xml']);body=root.find(q('body'))
paras=body.findall(q('p'))
def proto(style):
    return next(p for p in paras if p.find('w:pPr/w:pStyle',NS) is not None and p.find('w:pPr/w:pStyle',NS).get(q('val'))==style)
protos={s:deepcopy(proto(s)) for s in ['Title','Subtitle','Heading1','Heading2']}
protos['Normal']=deepcopy(next(p for p in paras if p.find('w:pPr/w:pStyle',NS) is None and p.find(q('r')) is not None))
tables={len(t.find(q('tr')).findall(q('tc'))):deepcopy(t) for t in body.findall(q('tbl'))}
sect=deepcopy(body.find(q('sectPr')))
for x in list(body): body.remove(x)
md=MD.read_text()
refs=dict(re.findall(r'^\[([^\]]+)\]: (.+)$',md,re.M))
rels=E.fromstring(parts['word/_rels/document.xml.rels'])
RNS='http://schemas.openxmlformats.org/package/2006/relationships'
linkids={}
for i,(key,url) in enumerate(refs.items(),100):
    rid='rIdCompare'+str(i);linkids[key]=rid
    r=E.SubElement(rels,'{'+RNS+'}Relationship');r.set('Id',rid);r.set('Type',NS['r']+'/hyperlink');r.set('Target',url);r.set('TargetMode','External')

def clear_content(p):
    for x in list(p):
        if x.tag!=q('pPr'):p.remove(x)

def add_text(p,s,bold=False,link=None,size=None):
    target=p
    if link:
        target=E.SubElement(p,q('hyperlink'));target.set('{'+NS['r']+'}id',linkids[link])
    r=E.SubElement(target,q('r'));pr=E.SubElement(r,q('rPr'))
    if bold:pr.append(el('b'))
    if size:pr.append(el('sz',val=size))
    if link:pr.append(el('color',val='245A81'))
    t=E.SubElement(r,q('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=s

def inline(p,text,bold=False,size=None):
    text=text.replace('**','')
    pos=0
    for m in re.finditer(r'\[([^\]]+)\]',text):
        ids=re.findall(r'(?<![A-Za-z0-9])(?:A(?![A-Za-z0-9])|[A-Z]\d+)\b',m.group(1))
        key=next((x for x in ids if x in refs),None)
        if not key:continue
        add_text(p,text[pos:m.start()],bold,size=size)
        add_text(p,m.group(0),bold,link=key,size=size);pos=m.end()
    add_text(p,text[pos:],bold,size=size)

def para(text,style='Normal'):
    p=deepcopy(protos[style]);clear_content(p)
    if p.find(q('pPr')) is None:p.insert(0,el('pPr'))
    if style=='Heading1':
        pp=p.find(q('pPr'))
        if pp.find(q('pageBreakBefore')) is None:pp.append(el('pageBreakBefore'))
    if style=='Title' and '对比分析报告' in text:
        first,last=text.split('对比分析报告',1)
        inline(p,first)
        r=E.SubElement(p,q('r'));E.SubElement(r,q('br'))
        inline(p,'对比分析报告'+last)
    else:inline(p,text)
    body.append(p);return p

def table(rows):
    n=len(rows[0]);t=deepcopy(tables[n]);oldrows=t.findall(q('tr'))
    # All tables inherit source properties; widths adapt to comparative content.
    widths=[2800,6838] if n==2 else [1700,3950,3988]
    grid=t.find(q('tblGrid'))
    for c,w in zip(grid,widths):c.set(q('w'),str(w))
    for r in oldrows:t.remove(r)
    for ri,row in enumerate(rows):
        r=deepcopy(oldrows[0] if ri==0 else oldrows[1])
        for ci,(cell,text) in enumerate(zip(r.findall(q('tc')),row)):
            props=cell.find(q('tcPr'));props.find(q('tcW')).set(q('w'),str(widths[ci]))
            sh=props.find(q('shd'));sh.set(q('fill'),'E8EEF4' if ri==0 else ('F7F8FA' if ri%2==0 else 'FFFFFF'))
            p=deepcopy(cell.find(q('p')))
            for x in list(cell):
                if x.tag!=q('tcPr'):cell.remove(x)
            clear_content(p);inline(p,text,bold=ri==0,size=18);cell.append(p)
        t.append(r)
    body.append(t)
    p=para('');pp=p.find(q('pPr'))
    if pp is None:pp=E.SubElement(p,q('pPr'))
    sp=pp.find(q('spacing'))
    if sp is None:sp=E.SubElement(pp,q('spacing'))
    sp.set(q('after'),'0');sp.set(q('line'),'60');sp.set(q('lineRule'),'exact')

META=json.loads((OUT/'sources/diagram-manifest.json').read_text())
FIG={f['key']:f for f in META}
EXTRA_NS={'wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','a':'http://schemas.openxmlformats.org/drawingml/2006/main','pic':'http://schemas.openxmlformats.org/drawingml/2006/picture'}
NS.update(EXTRA_NS)
def qn(name):
    prefix,local=name.split(':'); return '{'+NS[prefix]+'}'+local
def sub(parent,tag,**attrs):
    x=E.SubElement(parent,qn(tag))
    for k,v in attrs.items():x.set(qn(k) if ':' in k else k,str(v))
    return x
def rel(target,kind='hyperlink'):
    rid='rIdAttachment'+str(len(rels)+500)
    x=E.SubElement(rels,'{'+RNS+'}Relationship',Id=rid,Type=NS['r']+'/'+kind,Target=target)
    if kind=='hyperlink':x.set('TargetMode','External')
    return rid
def asset_links(items):
    p=para('')
    for i,(label,target) in enumerate(items):
        if i:add_text(p,'  ·  ',size=18)
        h=E.SubElement(p,q('hyperlink'));h.set('{'+NS['r']+'}id',rel(target))
        r=sub(h,'w:r');rp=sub(r,'w:rPr');sub(rp,'w:sz',**{'w:val':18});sub(rp,'w:color',**{'w:val':'245A81'});sub(r,'w:t').text=label
    return p

def figure(key):
    f=FIG[key];i=META.index(f)
    name=key+'.png';parts['word/media/'+name]=(OUT/'assets/report-diagrams'/name).read_bytes()
    rid=rel('media/'+name,'image')
    p=para('');pp=p.find(q('pPr'))
    if pp is None:pp=E.SubElement(p,q('pPr'))
    for tag in ['spacing','jc','keepNext','pageBreakBefore']:
        for x in pp.findall(q(tag)):pp.remove(x)
    pp.append(el('pageBreakBefore'));pp.append(el('keepNext'));pp.append(el('jc',val='center'))
    pp.append(el('spacing',before='0',after='180',line='240',lineRule='auto'))
    r=sub(p,'w:r');d=sub(r,'w:drawing');a=sub(d,'wp:inline',distT=0,distB=0,distL=0,distR=0)
    w=round(17/2.54*914400);h=round(w*f['height']/f['width'])
    sub(a,'wp:extent',cx=w,cy=h);sub(a,'wp:effectExtent',l=0,t=0,r=0,b=0)
    sub(a,'wp:docPr',id=200+i,name=f['title'],descr=f['caption']+' 来源 '+f['sources'])
    lock=sub(a,'wp:cNvGraphicFramePr');sub(lock,'a:graphicFrameLocks',noChangeAspect=1)
    g=sub(a,'a:graphic');data=sub(g,'a:graphicData',uri=NS['pic']);pic=sub(data,'pic:pic')
    nv=sub(pic,'pic:nvPicPr');sub(nv,'pic:cNvPr',id=200+i,name=name);sub(nv,'pic:cNvPicPr')
    fill=sub(pic,'pic:blipFill');sub(fill,'a:blip',**{'r:embed':rid});st=sub(fill,'a:stretch');sub(st,'a:fillRect')
    sp=sub(pic,'pic:spPr');tr=sub(sp,'a:xfrm');sub(tr,'a:off',x=0,y=0);sub(tr,'a:ext',cx=w,cy=h)
    geom=sub(sp,'a:prstGeom',prst='rect');sub(geom,'a:avLst')
    cap=para(f['title']);cpp=cap.find(q('pPr'))
    if cpp is None:cpp=E.SubElement(cap,q('pPr'));cap.insert(0,cpp)
    cpp.append(el('keepNext'))
    for run in cap.findall(q('r')):run.find(q('rPr')).append(el('b'))
    p=para(f['caption']+' 来源：'+f['sources']);cpp=p.find(q('pPr'))
    if cpp is None:cpp=E.SubElement(p,q('pPr'));p.insert(0,cpp)
    cpp.append(el('keepNext'))
    prefix='assets/report-diagrams/'+key
    asset_links([('PNG 原图',prefix+'.png'),('SVG 矢量图',prefix+'.svg'),('可编辑 draw.io',prefix+'.drawio')])

lines=md.splitlines();i=0
while i<len(lines):
    line=lines[i].strip()
    if not line or re.match(r'^\[[^\]]+\]: ',line): i+=1;continue
    if line.startswith('{{figure:'):
        figure(line.removeprefix('{{figure:').removesuffix('}}'));i+=1;continue
    if line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].startswith('|'):
            vals=[x.strip() for x in lines[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r'[-: ]+',x) for x in vals):rows.append(vals)
            i+=1
        table(rows);continue
    if line.startswith('# '):para(line[2:],'Title')
    elif line.startswith('## '):para(line[3:],'Heading1')
    elif line.startswith('### '):para(line[4:],'Heading2')
    elif line.startswith('**检查对象'):para(line,'Subtitle')
    else:para(line)
    i+=1
body.append(sect)
def xml(x):return E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
types=E.fromstring(parts['[Content_Types].xml'])
if not any(e.get('Extension')=='png' for e in types):E.SubElement(types,'{http://schemas.openxmlformats.org/package/2006/content-types}Default',Extension='png',ContentType='image/png')
parts['[Content_Types].xml']=xml(types)
parts['word/document.xml']=xml(root);parts['word/_rels/document.xml.rels']=xml(rels)
for name in list(parts):
    if re.fullmatch(r'word/footer\d+\.xml',name):
        parts[name]=parts[name].replace('2026 年 11 月 10 日'.encode(),'2026 年 11 月 15 日'.encode())
core=E.fromstring(parts['docProps/core.xml'])
for field,text in [('title',STEM),('subject','Codex Dot 与 WorkBuddy 执行环境对比和 GUI 体验分析')]:
    x=core.find('{http://purl.org/dc/elements/1.1/}'+field)
    if x is None:x=E.SubElement(core,'{http://purl.org/dc/elements/1.1/}'+field)
    x.text=text
parts['docProps/core.xml']=xml(core)
settings=E.fromstring(parts['word/settings.xml'])
update=settings.find(q('updateFields'))
if update is None:update=E.SubElement(settings,q('updateFields'))
update.set(q('val'),'true')
parts['word/settings.xml']=xml(settings)
with ZipFile(FINAL,'w',ZIP_DEFLATED) as z:
    for n,b in parts.items():z.writestr(n,b)
editable={'[Content_Types].xml','word/document.xml','word/_rels/document.xml.rels','word/footer1.xml','docProps/core.xml','word/settings.xml'}
with ZipFile(REF) as z:
    unchanged=[n for n in z.namelist() if n not in editable]
    assert all(parts[n]==z.read(n) for n in unchanged)
    inv={n:{'sha256':hashlib.sha256(parts[n]).hexdigest(),'bytes':len(parts[n]),'role':'editable' if n in editable else 'preserve'} for n in parts}
assert E.tostring(sect)==E.tostring(E.fromstring(ZipFile(REF).read('word/document.xml')).find('w:body/w:sectPr',NS))
(OUT/'sources/package-inventory.json').write_text(json.dumps(inv,indent=2))
(OUT/'sources/docx-validation.json').write_text(json.dumps({'source_sha256':hashlib.sha256(REF.read_bytes()).hexdigest(),'preserved_parts':len(unchanged),'sources':len(refs),'tables':len(body.findall(q('tbl'))),'chapters':12,'report_sha256':hashlib.sha256(FINAL.read_bytes()).hexdigest()},indent=2))
# Deliverable Markdown expands the same diagram definitions.
public_md=md
for f in META:
    prefix='assets/report-diagrams/'+f['key']
    block='![{title}]({prefix}.png)\n\n**{title}**\n\n{caption} 来源：{sources}\n\n[PNG 原图]({prefix}.png) · [SVG 矢量图]({prefix}.svg) · [可编辑 draw.io]({prefix}.drawio)'.format(prefix=prefix,**f)
    public_md=public_md.replace('{{figure:'+f['key']+'}}',block)
(OUT/(STEM+'.md')).write_text(public_md)
print(FINAL)
