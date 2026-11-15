from pathlib import Path

from html import escape

import xml.etree.ElementTree as ET

import json

import re

import subprocess

import zipfile

from PIL import Image, ImageFont

FONT = '/usr/share/fonts/NotoSansCJKsc-Single.otf'

C = {'ink': '#16324F', 'muted': '#52647A', 'blue': '#176B99', 'line': '#A9BED0',
     'pale': '#EFF6FB', 'white': '#FFFFFF', 'amber': '#A86C16', 'amberfill': '#FFF8E9',
     'teal': '#137B77', 'tealfill': '#EDF8F5', 'slate': '#64788C'}

class Figure:
    def __init__(self, key, title, subtitle, w, h):
        self.key, self.title, self.subtitle, self.w, self.h = key, title, subtitle, w, h
        self.nodes, self.edges, self.texts, self.groups = [], [], [], []

    def group(self, id, x, y, w, h, title, parent='1', fill='#F6F9FC'):
        self.groups.append(dict(id=id,x=x,y=y,w=w,h=h,title=title,parent=parent,fill=fill))

    def node(self, id, x, y, w, h, title, body=(), parent='1', kind='blue', size=26):
        self.nodes.append(dict(id=id,x=x,y=y,w=w,h=h,title=title,body=list(body),parent=parent,kind=kind,size=size))

    def edge(self, id, source, target, points, kind='blue', arrow=True, label=None):
        self.edges.append(dict(id=id,source=source,target=target,points=points,kind=kind,arrow=arrow,label=label))

    def text(self, id, x, y, w, h, lines, size=24, color=None, align='left', bold=False):
        self.texts.append(dict(id=id,x=x,y=y,w=w,h=h,lines=lines,size=size,color=color or C['muted'],align=align,bold=bold))

def font_width(text,size):
    return ImageFont.truetype(FONT,size).getlength(text)

def colors(kind):
    if kind=='amber':return C['amberfill'],C['amber']
    if kind=='teal':return C['tealfill'],C['teal']
    return C['pale'],C['blue']

def text_svg(lines,x,y,size,color,anchor='middle',bold=False,lineheight=None):
    lineheight=lineheight or size*1.5
    a=[]
    for i,line in enumerate(lines):
        a.append(f'<text x="{x}" y="{y+i*lineheight}" text-anchor="{anchor}" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}">{escape(line)}</text>')
    return '\n'.join(a)

def svg(fig):
    p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{fig.w}" height="{fig.h}" viewBox="0 0 {fig.w} {fig.h}">',
       '<title>'+escape(fig.title)+'</title>', '<desc>'+escape(fig.subtitle)+'</desc>',
       '<defs>']
    for kind in ['blue','teal','amber','slate']:
        p.append(f'<marker id="arrow-{kind}" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M 0 1 L 8 5 L 0 9 Z" fill="{C[kind]}"/></marker>')
    p += ['</defs>',f'<rect width="{fig.w}" height="{fig.h}" fill="white"/>',
          '<g font-family="Noto Sans CJK SC, Microsoft YaHei, sans-serif">',
          f'<rect x="40" y="42" width="7" height="38" rx="3" fill="{C["teal"]}"/>',
          text_svg([fig.title],64,75,34,C['ink'],'start',True),
          text_svg([fig.subtitle],64,112,22,C['muted'],'start')]
    for n in fig.groups:
        p.append(f'<rect x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" rx="18" fill="{n["fill"]}" stroke="{C["line"]}" stroke-width="1.5"/>')
        p.append(text_svg([n['title']],n['x']+24,n['y']+40,26,C['ink'],'start',True))
    for e in fig.edges:
        pts=' '.join(f'{x},{y}' for x,y in e['points'])
        dash=' stroke-dasharray="8 6"' if e['kind']=='amber' else ''
        marker=f' marker-end="url(#arrow-{e["kind"]})"' if e['arrow'] else ''
        p.append(f'<polyline points="{pts}" fill="none" stroke="{C[e["kind"]]}" stroke-width="2.3" stroke-linejoin="round"{dash}{marker}/>')
    for n in fig.nodes:
        fill,stroke=colors(n['kind'])
        dash=' stroke-dasharray="8 6"' if n['kind']=='amber' else ''
        p.append(f'<rect x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="1.6"{dash}/>')
        title_size=28
        block=title_size+len(n['body'])*(n['size']*1.45)+ (9 if n['body'] else 0)
        baseline=n['y']+(n['h']-block)/2+title_size*.87
        assert font_width(n['title'],title_size)<n['w']-24,(fig.key,n['title'])
        p.append(text_svg([n['title']],n['x']+n['w']/2,baseline,title_size,C['ink'],bold=True))
        for j,line in enumerate(n['body']):
            assert font_width(line,n['size'])<n['w']-22,(fig.key,line)
            p.append(text_svg([line],n['x']+n['w']/2,baseline+12+(j+1)*n['size']*1.45,n['size'],C['muted']))
    for e in fig.edges:
        if e['label']:
            x,y,label=e['label'];w=font_width(label,22)+20
            p.append(f'<rect x="{x-w/2}" y="{y-15}" width="{w}" height="28" rx="5" fill="white"/>')
            p.append(text_svg([label],x,y+5,22,C['blue']))
    for t in fig.texts:
        for line in t['lines']:assert font_width(line,t['size'])<=t['w'],(fig.key,line)
        p.append(text_svg(t['lines'],t['x']+(t['w']/2 if t['align']=='center' else 0),t['y']+t['size'],t['size'],t['color'],'middle' if t['align']=='center' else 'start',t['bold']))
    p.append('</g></svg>')
    return '\n'.join(p)

def mxmodel(fig):
    model=ET.Element('mxGraphModel',dx=str(fig.w),dy=str(fig.h),grid='1',gridSize='10',guides='1',tooltips='1',connect='1',arrows='1',fold='1',page='1',pageScale='1',pageWidth=str(fig.w),pageHeight=str(fig.h),math='0',shadow='0')
    root=ET.SubElement(model,'root'); ET.SubElement(root,'mxCell',id='0'); ET.SubElement(root,'mxCell',id='1',parent='0')
    lookup={n['id']:n for n in fig.nodes+fig.groups}
    def vertex(id,value,style,x,y,w,h,parent='1'):
        c=ET.SubElement(root,'mxCell',id=id,value=value,style=style,vertex='1',parent=parent)
        if parent!='1':x-=lookup[parent]['x'];y-=lookup[parent]['y']
        ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
    def textcell(id,x,y,w,h,lines,size,color,bold=False,align='left'):
        value='<div style="line-height:1.5">'+'<br>'.join(escape(s) for s in lines)+'</div>'
        vertex(id,value,f'text;html=1;strokeColor=none;fillColor=none;align={align};verticalAlign=top;whiteSpace=wrap;rounded=0;fontFamily=Noto Sans CJK SC;fontSize={size};fontColor={color};fontStyle={1 if bold else 0};spacing=0;',x,y,w,h)
    textcell('title',64,41,fig.w-100,45,[fig.title],34,C['ink'],True)
    textcell('subtitle',64,85,fig.w-100,30,[fig.subtitle],22,C['muted'])
    vertex('accent','',f'rounded=1;fillColor={C["teal"]};strokeColor=none;',40,42,7,38)
    for n in fig.groups:
        style=f'rounded=1;arcSize=8;whiteSpace=wrap;html=1;fillColor={n["fill"]};strokeColor={C["line"]};strokeWidth=1.5;align=left;verticalAlign=top;spacingLeft=24;spacingTop=16;fontFamily=Noto Sans CJK SC;fontSize=26;fontStyle=1;fontColor={C["ink"]};container=1;collapsible=0;recursiveResize=0;'
        vertex(n['id'],escape(n['title']),style,n['x'],n['y'],n['w'],n['h'],n['parent'])
    for n in fig.nodes:
        fill,stroke=colors(n['kind']);ts=28
        value=f'<div style="font-size:{ts}px;font-weight:bold;line-height:1.3">{escape(n["title"])}</div>'
        if n['body']:value+=f'<div style="margin-top:9px;font-size:{n["size"]}px;line-height:1.45;color:{C["muted"]}">'+'<br>'.join(escape(s) for s in n['body'])+'</div>'
        style=f'rounded=1;arcSize=12;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth=1.6;align=center;verticalAlign=middle;fontFamily=Noto Sans CJK SC;fontColor={C["ink"]};spacing=10;'
        if n['kind']=='amber':style+='dashed=1;dashPattern=8 6;'
        vertex(n['id'],value,style,n['x'],n['y'],n['w'],n['h'],n['parent'])
    for e in fig.edges:
        src,dst=lookup[e['source']],lookup[e['target']]
        sx,sy=e['points'][0];tx,ty=e['points'][-1]
        style=f'edgeStyle=none;rounded=0;html=1;strokeColor={C[e["kind"]]};strokeWidth=2.3;endArrow={"block" if e["arrow"] else "none"};endFill=1;exitX={(sx-src["x"])/src["w"]};exitY={(sy-src["y"])/src["h"]};exitPerimeter=0;entryX={(tx-dst["x"])/dst["w"]};entryY={(ty-dst["y"])/dst["h"]};entryPerimeter=0;'
        if e['kind']=='amber':style+='dashed=1;dashPattern=8 6;'
        c=ET.SubElement(root,'mxCell',id=e['id'],style=style,edge='1',parent='1',source=e['source'],target=e['target'])
        g=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
        if len(e['points'])>2:
            arr=ET.SubElement(g,'Array',attrib={'as':'points'})
            for x,y in e['points'][1:-1]:ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
        if e['label']:
            x,y,label=e['label'];w=font_width(label,22)+20
            vertex(e['id']+'-label',escape(label),f'text;html=1;fillColor=#FFFFFF;strokeColor=none;align=center;verticalAlign=middle;fontFamily=Noto Sans CJK SC;fontSize=22;fontColor={C["blue"]};',x-w/2,y-15,w,28)
    for t in fig.texts:textcell(t['id'],t['x'],t['y'],t['w'],t['h'],t['lines'],t['size'],t['color'],t['bold'],t['align'])
    return model

def drawio(figures,path):
    doc=ET.Element('mxfile',host='app.diagrams.net',type='device',version='24.7.17')
    for f in figures:
        d=ET.SubElement(doc,'diagram',id=f.key,name=f.title)
        d.append(mxmodel(f))
    ET.indent(doc,space='  ')
    ET.ElementTree(doc).write(path,encoding='utf-8',xml_declaration=True)

def embed(f):
    folder='assets/report-diagrams/'
    return f'![{f.title}]({folder}{f.key}.png)\n\n[SVG 矢量图]({folder}{f.key}.svg) · [可编辑 draw.io 源文件]({folder}{f.key}.drawio)'
