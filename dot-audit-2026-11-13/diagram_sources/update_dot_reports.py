from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from copy import deepcopy
from lxml import etree as E
import re,json,hashlib

BASE=Path(__file__).resolve().parents[1]
WORK=BASE/'diagram_sources'
STEM='Dot云电脑软硬件配置与运行检查报告'
META=json.loads((WORK/'diagram-manifest.json').read_text())
ORIGINAL_MD=(WORK/'report-before-diagrams-2026-11-15.md').read_text()
REF=WORK/'report-before-diagrams-2026-11-15.docx'
with ZipFile(REF) as z:parts={n:z.read(n) for n in z.namelist()}
original_parts=dict(parts)

notice='图件补充日期：2026 年 11 月 15 日。新增 8 张逻辑图；历史检查与原公开资料核查日期保持不变，未新增远程实测。'
md=ORIGINAL_MD
for chapter in sorted({f['chapter'] for f in META}):
    anchor=re.search(r'^## '+str(chapter+1)+r' .+$',md,re.M).group(0)
    blocks=[]
    for f in [f for f in META if f['chapter']==chapter]:
        prefix='assets/report-diagrams/'+f['key']
        blocks.append(f'<!-- diagram:{f["key"]} -->\n\n![{f["title"]}]({prefix}.png)\n\n{f["caption"]} 来源：{f["sources"]}\n\n[PNG 原图]({prefix}.png) · [SVG 矢量图]({prefix}.svg) · [可编辑 draw.io 源文件]({prefix}.drawio)\n\n<!-- /diagram:{f["key"]} -->')
    md=md.replace(anchor,'\n\n'.join(blocks)+'\n\n'+anchor,1)
marker='历史观察日期：2026 年 11 月 11 日。检查性质：对话证据复核与技术分析，未连接目标云电脑重新实测。'
md=md.replace(marker,marker+'\n\n<!-- figure-update-notice -->\n'+notice+'\n\n**图件附件：** [完整可编辑图集（8 页）](assets/report-diagrams/Dot云电脑完整图集.drawio) · [图片与源文件说明](图件说明与来源索引.md)。正文内直接展示 PNG，每图附 SVG 和可编辑 draw.io。图中的实线仅表示相应来源支持的逻辑关系，不自动代表现场实测；证据等级见图例和图注。\n<!-- /figure-update-notice -->',1)
(BASE/(STEM+'.md')).write_text(md)

NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','a':'http://schemas.openxmlformats.org/drawingml/2006/main','pic':'http://schemas.openxmlformats.org/drawingml/2006/picture'}
RNS='http://schemas.openxmlformats.org/package/2006/relationships'
CT='http://schemas.openxmlformats.org/package/2006/content-types'
def q(name):
    prefix,local=name.split(':');return '{'+NS[prefix]+'}'+local
def sub(parent,tag,**attrs):
    x=E.SubElement(parent,q(tag))
    for k,v in attrs.items():x.set(q(k) if ':' in k else k,str(v))
    return x
doc=E.fromstring(parts['word/document.xml']);body=doc.find('w:body',NS)
original_children=list(body)
child_snapshots=[E.tostring(x) for x in original_children]
rels=E.fromstring(parts['word/_rels/document.xml.rels'])
types=E.fromstring(parts['[Content_Types].xml'])
refs=dict(re.findall(r'^\[([^\]]+)\]: (.+)$',ORIGINAL_MD,re.M))
targets={x.get('Target'):x.get('Id') for x in rels}
newrels=[]
def relation(target,type_='hyperlink'):
    if target in targets:return targets[target]
    rid='rIdFigure'+str(500+len(newrels))
    attrib={'Id':rid,'Type':NS['r']+'/'+type_,'Target':target}
    if type_=='hyperlink':attrib['TargetMode']='External'
    E.SubElement(rels,'{'+RNS+'}Relationship',attrib)
    targets[target]=rid;newrels.append(attrib);return rid
normal=next(x for x in original_children if x.tag==q('w:p') and x.find('w:pPr/w:pStyle',NS) is None and x.find('w:r',NS) is not None)
def p(text='',bold=False,size=20,keep=False):
    x=deepcopy(normal)
    for child in list(x):
        if child.tag!=q('w:pPr'):x.remove(child)
    pp=x.find('w:pPr',NS)
    if pp is None:pp=E.SubElement(x,q('w:pPr'))
    for tag in ['w:keepNext','w:pageBreakBefore']:
        for old in pp.findall(tag,NS):pp.remove(old)
    if keep:sub(pp,'w:keepNext')
    def run(s,url=None):
        if not s:return
        parent=x
        if url:parent=sub(x,'w:hyperlink',**{'r:id':relation(url)})
        r=sub(parent,'w:r');rp=sub(r,'w:rPr')
        sub(rp,'w:sz',**{'w:val':size})
        if bold:sub(rp,'w:b')
        if url:sub(rp,'w:color',**{'w:val':'245A81'})
        t=sub(r,'w:t');t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=s
    pos=0
    for m in re.finditer(r'\[([^\]]+)\]',text):
        ids=re.findall(r'(?<![A-Za-z0-9])(?:[AB](?![A-Za-z0-9])|[OTC]\d+)\b',m.group(1))
        key=next((k for k in ids if k in refs),None)
        if key:
            run(text[pos:m.start()]);run(m.group(0),refs[key]);pos=m.end()
    run(text[pos:]);return x
def link_p(items):
    x=p('',size=18)
    for i,(label,target) in enumerate(items):
        if i:
            r=sub(x,'w:r');sub(r,'w:t').text='  ·  '
        h=sub(x,'w:hyperlink',**{'r:id':relation(target)})
        r=sub(h,'w:r');rp=sub(r,'w:rPr');sub(rp,'w:sz',**{'w:val':18});sub(rp,'w:color',**{'w:val':'245A81'})
        sub(r,'w:t').text=label
    return x

def figure(f,i):
    name=f['key']+'.png'
    parts['word/media/'+name]=(BASE/'assets/report-diagrams'/name).read_bytes()
    rid=relation('media/'+name,'image')
    width=round(17/2.54*914400);height=round(width*f['height']/f['width'])
    x=p('',keep=True);pp=x.find('w:pPr',NS)
    for tag in ['w:spacing','w:jc']:
        for old in pp.findall(tag,NS):pp.remove(old)
    sub(pp,'w:pageBreakBefore');sub(pp,'w:jc',**{'w:val':'center'})
    sub(pp,'w:spacing',**{'w:before':'0','w:after':'180','w:line':'240','w:lineRule':'auto'})
    r=sub(x,'w:r');drawing=sub(r,'w:drawing')
    inline=sub(drawing,'wp:inline',distT=0,distB=0,distL=0,distR=0)
    sub(inline,'wp:extent',cx=width,cy=height)
    sub(inline,'wp:effectExtent',l=0,t=0,r=0,b=0)
    sub(inline,'wp:docPr',id=100+i,name=f['title'],descr=f['caption']+' 来源 '+f['sources'])
    locks=sub(inline,'wp:cNvGraphicFramePr');sub(locks,'a:graphicFrameLocks',noChangeAspect=1)
    graphic=sub(inline,'a:graphic');data=sub(graphic,'a:graphicData',uri=NS['pic'])
    pic=sub(data,'pic:pic');nv=sub(pic,'pic:nvPicPr');sub(nv,'pic:cNvPr',id=100+i,name=name);sub(nv,'pic:cNvPicPr')
    fill=sub(pic,'pic:blipFill');sub(fill,'a:blip',**{'r:embed':rid});stretch=sub(fill,'a:stretch');sub(stretch,'a:fillRect')
    sp=sub(pic,'pic:spPr');transform=sub(sp,'a:xfrm');sub(transform,'a:off',x=0,y=0);sub(transform,'a:ext',cx=width,cy=height)
    geom=sub(sp,'a:prstGeom',prst='rect');sub(geom,'a:avLst')
    prefix='assets/report-diagrams/'+f['key']
    return [x,p(f['title'],bold=True,keep=True),p(f['caption']+' 来源：'+f['sources'],keep=True),link_p([('PNG 原图',prefix+'.png'),('SVG 矢量图',prefix+'.svg'),('可编辑 draw.io 源文件',prefix+'.drawio')])]

for i,f in enumerate(META):
    chapter=f['chapter']+1
    anchor=next(x for x in original_children if ''.join(x.itertext()).startswith(str(chapter)+' ') and x.find('w:pPr/w:pStyle',NS) is not None)
    index=list(body).index(anchor)
    for el in figure(f,i):body.insert(index,el);index+=1

meta_anchor=next(x for x in original_children if ''.join(x.itertext()).startswith('历史观察日期：'))
idx=list(body).index(meta_anchor)+1
body.insert(idx,p(notice,size=18))
body.insert(idx+1,link_p([('完整可编辑图集（8 页）','assets/report-diagrams/Dot云电脑完整图集.drawio'),('图片与源文件说明','图件说明与来源索引.md')]))
if not any(x.get('Extension')=='png' for x in types):E.SubElement(types,'{'+CT+'}Default',Extension='png',ContentType='image/png')
def xml(x):return E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
parts['word/document.xml']=xml(doc)
parts['word/_rels/document.xml.rels']=xml(rels)
parts['[Content_Types].xml']=xml(types)
parts['word/footer1.xml']=parts['word/footer1.xml'].replace('2026 年 11 月 13 日'.encode(),'2026 年 11 月 15 日'.encode())
assert child_snapshots==[E.tostring(x) for x in original_children]
preserve=set(original_parts)-{'word/document.xml','word/_rels/document.xml.rels','[Content_Types].xml','word/footer1.xml'}
assert all(parts[k]==original_parts[k] for k in preserve)
final=BASE/(STEM+'.docx')
with ZipFile(final,'w',ZIP_DEFLATED) as z:
    for n,b in parts.items():z.writestr(n,b)

readme=['# Dot 报告图件与来源索引','',notice,'','## 文件与使用方式','',
'- 报告提供 Word 与 Markdown 两版，正文嵌入 PNG。','- 每图提供 2 倍分辨率 PNG、纯矢量 SVG 与单页 draw.io。',
'- assets/report-diagrams/Dot云电脑完整图集.drawio 含 8 页；用 diagrams.net 或 draw.io 打开后，框、文字、容器和连接线均可编辑。',
'- 解压完整压缩包并保持 assets 子目录位置，可使用报告中的相对图片链接。Word 的图片已内嵌，即使单独复制也能显示。',
'- 图下注释与本索引沿用原报告来源编号。原始个人聊天附件与旧报告不包含在此包中，本地证据链接仍依赖原项目路径。','',
'## 证据图例','',
'蓝色通常表示历史记录，青色表示明确标注的官方能力或用户确认；橙色虚线表示未确认、待核验或建议。各图局部图例优先。实线不是现场实测标签，不证明物理部署或完整流量链路。原报告调查结论、表格和来源未替换。','',
'## 图件目录','']
for f in META:
    prefix='assets/report-diagrams/'+f['key']
    readme += [f'### {f["title"]}','',f['caption']+' 来源：'+f['sources'],'',f'[PNG]({prefix}.png) · [SVG]({prefix}.svg) · [draw.io]({prefix}.drawio)','']
readme+=['## 原报告来源链接','']
for key,url in refs.items():readme.append(f'- [{key}]({url})')
(BASE/'图件说明与来源索引.md').write_text('\n'.join(readme)+'\n')
for f in META:
    f['png_size']=[f['width']*2,f['height']*2]
validation={'images':len(META),'preserved_original_body_elements':len(original_children),'preserved_package_parts':len(preserve),'original_docx_sha256':hashlib.sha256(REF.read_bytes()).hexdigest(),'report_docx_sha256':hashlib.sha256(final.read_bytes()).hexdigest(),'sources':len(refs),'original_tables':len(body.findall('w:tbl',NS))}
(WORK/'update-validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2))
print(json.dumps(validation,ensure_ascii=False,indent=2))
