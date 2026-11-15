from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
import math

OUT = Path(__file__).parent
W, H = 1660, 2170
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
INK, LINE = '#183348', '#516778'
nodes = {}
edges = []
texts = []
cards = []

def node(i, cx, y, w, h, label, kind='decision', fill='#F4F7FA', stroke=LINE, size=27):
    nodes[i] = dict(x=cx-w/2, y=y, w=w, h=h, label=label, kind=kind, fill=fill, stroke=stroke, size=size)

def edge(i, a, b, pts, label='', lx=0, ly=0, color=LINE):
    edges.append(dict(id=i,a=a,b=b,pts=pts,label=label,lx=lx,ly=ly,color=color))

node('start',830,100,360,65,'开始：AI 需要电脑执行任务','terminal',size=24)
node('os',830,200,400,220,'必须依赖\n哪种操作系统？')
node('win_gate',280,580,400,220,'本地方案不合适\n且任务适合上云？',fill='#FFF5E9',stroke='#B86A13',size=26)
node('general_gate',830,580,400,220,'是否需要且适合\n云端执行？',size=26)
node('mac_gate',1380,580,400,220,'本地方案不合适\n且任务适合上云？',size=26)
node('win_cloud',280,1350,400,90,'Windows 云电脑','terminal','#FFF0DD','#B86A13',31)
node('linux_cloud',830,1350,400,90,'Linux 云电脑','terminal','#EAF5F3','#257D70',31)
node('mac_cloud',1380,1350,400,90,'Mac 云电脑','terminal','#EDF3FB','#45688E',31)
node('local_choice',830,1560,400,180,'哪种本地设备\n更方便？')
node('win_local',280,1930,400,90,'本地 Windows 电脑','terminal','#EDF3FB','#45688E',29)
node('mac_local',1380,1930,400,90,'本地 Mac 电脑','terminal','#EDF3FB','#45688E',29)
edge('e1','start','os',[(830,165),(830,200)])
edge('e2','os','win_gate',[(630,310),(600,310),(600,480),(280,480),(280,580)],'必须 Windows',420,480,'#B86A13')
edge('e3','os','general_gate',[(830,420),(830,580)],'无专属系统依赖',830,500)
edge('e4','os','mac_gate',[(1030,310),(1060,310),(1060,480),(1380,480),(1380,580)],'必须 macOS',1230,480)
edge('e5','win_gate','win_cloud',[(480,690),(530,690),(530,1395),(480,1395)],'是',510,650,'#B86A13')
edge('e6','win_gate','win_local',[(80,690),(40,690),(40,1975),(80,1975)],'否',60,650)
edge('e7','general_gate','linux_cloud',[(1030,690),(1080,690),(1080,1395),(1030,1395)],'是',1060,650)
edge('e8','general_gate','local_choice',[(630,690),(590,690),(590,1490),(830,1490),(830,1560)],'否',610,650)
edge('e9','mac_gate','mac_cloud',[(1580,690),(1630,690),(1630,1395),(1580,1395)],'是',1610,650)
edge('e10','mac_gate','mac_local',[(1180,690),(1140,690),(1140,1490),(1630,1490),(1630,1975),(1580,1975)],'否',1160,650)
edge('e11','local_choice','win_local',[(630,1650),(280,1650),(280,1930)],'Windows',460,1650)
edge('e12','local_choice','mac_local',[(1030,1650),(1380,1650),(1380,1930)],'Mac',1200,1650)
texts = [
 ('title',40,20,1580,55,'AI 执行环境选择流程 · 先判断操作系统依赖',38,INK,True),
 ('win_note',80,1450,460,40,'Windows 刚需 + 本地不合适 + 云端可行',21,'#99580E',True),
 ('linux_note',630,1450,460,40,'无专属依赖 + 云端有需求且可行',21,'#257D70',True),
 ('mac_note',1180,1450,460,40,'macOS 刚需 + 本地不合适 + 云端可行',21,'#45688E',True),
 ('win_local_note',80,2030,460,40,'Windows 适用 + 本地够用或需留本地',21,'#45688E',True),
 ('mac_local_note',1180,2030,460,40,'macOS 适用 + 本地够用或需留本地',21,'#45688E',True),
 ('foot1',40,2070,1580,40,'本地 Windows 包含物理机、备用机、专用主机及本地 Windows 虚拟机。',24,LINE,False),
 ('foot2',40,2115,1580,40,'“否”可能表示本地已够用，也可能表示不能上云；后者需补足本地条件或调整任务。',24,LINE,False),
]
def card(i,x,y,w,h,title,lines,accent=LINE,line_height=36):
    cards.append(dict(id=i,x=x,y=y,w=w,h=h,title=title,lines=lines,accent=accent,line_height=line_height))
card('windows_examples',50,150,500,280,'必须 Windows 的典型任务',[
    ('• Windows 专属财务、ERP 软件',False),
    ('• 依赖 COM / ActiveX 的 Excel 流程',False),
    ('• Windows 原生界面操作或测试',False),
    ('网页或 API 能替代时，可重判依赖。',True),
], '#B86A13')
card('mac_examples',1110,150,500,280,'必须 macOS 的典型任务',[
    ('• Xcode 构建、签名及测试',False),
    ('• macOS 独有软件或桌面功能',False),
    ('生成 Word / Excel 文件本身，',False),
    ('不代表必须用 Windows 或 macOS。',True),
])
local_lines=[
    ('• 关机休眠，不能持续或定时运行',False),
    ('• AI 占用桌面，影响本人工作',False),
    ('• 资源不足，不愿升级或维护专用机',False),
    ('• 备用机或虚拟机也无法满足需求',False),
    ('上云还须同时满足',True),
    ('• 数据与软件授权允许',False),
    ('• 内网、账号、文件和外设可访问',False),
    ('• AI 可操作；预算、算力符合要求',False),
    ('• 会话时长、持久化满足任务',False),
    ('本地已够用，就不必上云。',True),
]
card('windows_conditions',50,835,460,470,'本地不合适的典型情况',local_lines,'#B86A13')
card('mac_conditions',1150,835,460,470,'本地不合适的典型情况',local_lines)
card('general_conditions',600,835,460,490,'通用任务的判断依据',[
    ('• 网页、API、Python、数据处理',False),
    ('• 所需功能和依赖可在 Linux 运行',False),
    ('云端需求',True),
    ('• 定时、并发、隔离或远程协作',False),
    ('上云还须同时满足',True),
    ('• 数据、授权、网络和外设允许',False),
    ('• AI 可操作；预算、算力适合',False),
    ('• 会话时长和持久化满足任务',False),
    ('临时任务或本地已够用，选“否”。',True),
    ('云环境不等于可以长期在线。',False),
    ('厂商为何常选 Linux？',True),
    ('通用任务够用；易批量部署与隔离；',False),
    ('授权与运维负担通常较低。',False),
],line_height=30)
card('local_examples',580,1780,500,230,'本地选哪台？看现有条件',[
    ('临时交互、依赖本地文件或外设、',False),
    ('数据不能上云，或本地设备已够用时，',False),
    ('选软件齐全、授权可用，且 AI 能操作',False),
    ('的 Windows 电脑或 Mac。',False),
])
annotations = [
    ('win_gate','windows_conditions',280,800,835),
    ('general_gate','general_conditions',830,800,835),
    ('mac_gate','mac_conditions',1380,800,835),
    ('local_choice','local_examples',830,1740,1780),
]

doc = ET.Element('mxfile', host='app.diagrams.net', type='device', version='24.7.17')
diagram = ET.SubElement(doc,'diagram',id='ai-environment-selection',name='AI 执行环境选择流程')
model = ET.SubElement(diagram,'mxGraphModel',dx=str(W),dy=str(H),grid='1',gridSize='10',guides='1',connect='1',arrows='1',page='1',pageScale='1',pageWidth=str(W),pageHeight=str(H),background='#FFFFFF')
root=ET.SubElement(model,'root')
ET.SubElement(root,'mxCell',id='0'); ET.SubElement(root,'mxCell',id='1',parent='0')

def vertex(i,value,style,x,y,w,h):
    c=ET.SubElement(root,'mxCell',id=i,value=value,style=style,vertex='1',parent='1')
    ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})

for i,n in nodes.items():
    shape='rhombus;' if n['kind']=='decision' else 'rounded=1;arcSize=50;absoluteArcSize=1;'
    style=shape+f"whiteSpace=wrap;html=0;fillColor={n['fill']};strokeColor={n['stroke']};strokeWidth=2;fontFamily=Noto Sans CJK SC;fontSize={n['size']};fontColor={INK};align=center;verticalAlign=middle;spacing=4;"
    vertex(i,n['label'],style,n['x'],n['y'],n['w'],n['h'])
for e in edges:
    a,b=nodes[e['a']],nodes[e['b']]
    (sx,sy),(tx,ty)=e['pts'][0],e['pts'][-1]
    style=f"edgeStyle=none;rounded=0;endArrow=block;endFill=1;endSize=10;strokeColor={e['color']};strokeWidth=2;exitX={(sx-a['x'])/a['w']};exitY={(sy-a['y'])/a['h']};exitPerimeter=0;entryX={(tx-b['x'])/b['w']};entryY={(ty-b['y'])/b['h']};entryPerimeter=0;"
    c=ET.SubElement(root,'mxCell',id=e['id'],source=e['a'],target=e['b'],edge='1',parent='1',style=style)
    geo=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
    if len(e['pts'])>2:
        ar=ET.SubElement(geo,'Array',attrib={'as':'points'})
        for x,y in e['pts'][1:-1]: ET.SubElement(ar,'mxPoint',x=str(x),y=str(y))
    if e['label']:
        width=ImageFont.truetype(FONT,25).getlength(e['label'])+18
        vertex(e['id']+'-label',e['label'],f'text;html=0;align=center;verticalAlign=middle;fillColor=#FFFFFF;strokeColor=none;fontFamily=Noto Sans CJK SC;fontSize=25;fontColor={e["color"]};',e['lx']-width/2,e['ly']-18,width,36)
for i,x,y,w,h,t,size,color,bold in texts:
    vertex(i,t,f'text;html=0;whiteSpace=wrap;align=left;verticalAlign=middle;fillColor=none;strokeColor=none;fontFamily=Noto Sans CJK SC;fontSize={size};fontColor={color};fontStyle={1 if bold else 0};',x,y,w,h)
for c in cards:
    vertex(c['id'],'',f"rounded=1;arcSize=18;absoluteArcSize=1;fillColor=#F7F9FC;strokeColor=#D5DEE8;strokeWidth=1;",c['x'],c['y'],c['w'],c['h'])
    vertex(c['id']+'-title',c['title'],f"text;html=0;align=left;verticalAlign=middle;fontFamily=Noto Sans CJK SC;fontSize=26;fontStyle=1;fontColor={c['accent']};",c['x']+24,c['y']+16,c['w']-48,40)
    for j,(line,bold) in enumerate(c['lines']):
        color = '#257D70' if c['id']=='general_conditions' and j>=10 else INK
        vertex(c['id']+f'-line{j}',line,f'text;html=0;align=left;verticalAlign=middle;fontFamily=Noto Sans CJK SC;fontSize=24;fontStyle={1 if bold else 0};fontColor={color};',c['x']+24,c['y']+68+j*c['line_height'],c['w']-48,36)
for a,b,x,y1,y2 in annotations:
    c=ET.SubElement(root,'mxCell',id='note-'+a,source=a,target=b,edge='1',parent='1',style='edgeStyle=none;dashed=1;endArrow=none;strokeColor=#98A9B9;strokeWidth=1;exitX=0.5;exitY=1;exitPerimeter=0;entryX=0.5;entryY=0;entryPerimeter=0;')
    ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
ET.indent(doc,space='  ')
ET.ElementTree(doc).write(OUT/'ai-computer-selection.drawio',encoding='utf-8',xml_declaration=True)

# Render from the same geometry; every diagram object remains editable in Draw.io.
S=2
im=Image.new('RGB',(W*S,H*S),'white'); d=ImageDraw.Draw(im)
def font(sz,bold=False): return ImageFont.truetype(BOLD if bold else FONT,round(sz*S))
def centered(label,cx,cy,sz,color):
    d.multiline_text((cx*S,cy*S),label,font=font(sz),fill=color,anchor='mm',align='center',spacing=8*S)
for e in edges:
    pts=[(x*S,y*S) for x,y in e['pts']]
    d.line(pts,fill=e['color'],width=3*S)
    x,y=e['pts'][-1]; px,py=e['pts'][-2]
    ang=math.atan2(y-py,x-px)
    arr=[(x*S,y*S)]+[((x-14*math.cos(ang)+s*6*math.sin(ang))*S,(y-14*math.sin(ang)-s*6*math.cos(ang))*S) for s in [-1,1]]
    d.polygon(arr,fill=e['color'])
for n in nodes.values():
    x,y,w,h=n['x'],n['y'],n['w'],n['h']
    if n['kind']=='decision':
        points=[((x+w/2)*S,y*S),((x+w)*S,(y+h/2)*S),((x+w/2)*S,(y+h)*S),(x*S,(y+h/2)*S)]
        d.polygon(points,fill=n['fill']); d.line(points+[points[0]],fill=n['stroke'],width=2*S)
    else:d.rounded_rectangle((x*S,y*S,(x+w)*S,(y+h)*S),radius=30*S,fill=n['fill'],outline=n['stroke'],width=2*S)
    centered(n['label'],x+w/2,y+h/2,n['size'],INK)
for e in edges:
    if e['label']:
        f=font(25); x,y=e['lx']*S,e['ly']*S
        box=d.textbbox((x,y),e['label'],font=f,anchor='mm')
        d.rectangle((box[0]-6*S,box[1]-3*S,box[2]+6*S,box[3]+3*S),fill='white')
        d.text((x,y),e['label'],font=f,fill=e['color'],anchor='mm')
for i,x,y,w,h,t,size,color,bold in texts:
    assert font(size,bold).getlength(t)<=w*S,(i,t)
    d.text((x*S,(y+h/2)*S),t,font=font(size,bold),fill=color,anchor='lm')
for c in cards:
    x,y,w,h=c['x'],c['y'],c['w'],c['h']
    d.rounded_rectangle((x*S,y*S,(x+w)*S,(y+h)*S),radius=18*S,fill='#F7F9FC',outline='#D5DEE8',width=S)
    assert font(26,True).getlength(c['title']) <= (w-48)*S
    d.text(((x+24)*S,(y+36)*S),c['title'],font=font(26,True),fill=c['accent'],anchor='lm')
    for j,(line,bold) in enumerate(c['lines']):
        assert font(24,bold).getlength(line)<=(w-48)*S,(c['id'],line)
        assert 68+j*c['line_height']+36<=h
        color = '#257D70' if c['id']=='general_conditions' and j>=10 else INK
        d.text(((x+24)*S,(y+86+j*c['line_height'])*S),line,font=font(24,bold),fill=color,anchor='lm')
for a,b,x,y1,y2 in annotations:
    for yy in range(y1,y2,10):
        d.line((x*S,yy*S,x*S,min(yy+5,y2)*S),fill='#98A9B9',width=2*S)
im.save(OUT/'ai-computer-selection.png',dpi=(192,192))
im.resize((996,1302)).save(OUT/'preview.png')
print('Created editable Draw.io and PNG:',im.size)
