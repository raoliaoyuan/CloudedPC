from pathlib import Path
from html import escape
import xml.etree.ElementTree as ET
import json
import re
import subprocess
import zipfile
from PIL import Image, ImageFont

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'assets' / 'report-diagrams'
OUT.mkdir(parents=True, exist_ok=True)
REPORT = BASE / '腾讯云CVM-Linux容器开发环境综合检查报告.md'
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

    def node(self, id, x, y, w, h, title, body=(), parent='1', kind='blue', size=19):
        self.nodes.append(dict(id=id,x=x,y=y,w=w,h=h,title=title,body=list(body),parent=parent,kind=kind,size=size))

    def edge(self, id, source, target, points, kind='blue', arrow=True, label=None):
        self.edges.append(dict(id=id,source=source,target=target,points=points,kind=kind,arrow=arrow,label=label))

    def text(self, id, x, y, w, h, lines, size=18, color=None, align='left', bold=False):
        self.texts.append(dict(id=id,x=x,y=y,w=w,h=h,lines=lines,size=size,color=color or C['muted'],align=align,bold=bold))


service = Figure('01-service-structure','图 5-1  服务管理结构',
    'Supervisor 配置与运行进程对应关系｜检查日期：2026-11-10',1400,850)
service.group('work',40,160,1320,600,'WorkBuddy 执行容器 · 064f56bb22e3')
service.node('init',500,225,400,88,'docker-init',['容器 PID 1'],parent='work')
service.node('supervisor',500,365,400,92,'supervisord',['平台主要服务管理器'],parent='work',kind='teal')
service.edge('e-init','init','supervisor',[(700,313),(700,365)])
cards=[
 ('terminal','平台终端与 API',['terminal / api / proxy','65310 / 65213 / 65216']),
 ('envd','执行环境管理',['e2b-envd','进程、文件及环境配置']),
 ('docker','内部 Docker',['dockerd / containerd','容器内开发运行时']),
 ('buddy','CodeBuddy 组件',['sandbox-proxy','CodeBuddy / MCP']),
 ('docs','同步与文档',['sync-server','editor-sdk']),
 ('logs','日志采集转发',['log-forward-tee','sandbox-log-collector']),
]
for i,(id,title,body) in enumerate(cards):
    x=50+i*220
    service.node(id,x,555,200,145,title,body,parent='work',size=16)
    service.edge('e-'+id,'supervisor',id,[(700,457),(700,505),(x+100,505),(x+100,555)])
service.text('note',50,785,1300,38,['注：部分服务受平台开关控制；一次性初始化任务、按需服务和 OpenSSH 启动保障见正文。'],18)

network = Figure('02-network-topology','图 7-1  容器网络逻辑图',
    '平台业务网络、已观察连接及条件性通信路径｜检查日期：2026-11-10',1600,1510)
network.text('legend',50,125,1500,32,['蓝色实线：已观察路径    灰色连线：内部接口关联    橙色虚线：推测或未验证'],18)
network.group('platform',40,190,1520,1050,'腾讯云 CVM / WorkBuddy 平台运行环境 · 部署位置为逻辑表达')
network.group('container',350,450,1160,660,'WorkBuddy 执行容器 · 064f56bb22e3',parent='platform',fill='#FFFFFF')
network.node('control',100,250,360,110,'平台管理组件',['具体进程及部署位置待确认'],parent='platform',kind='amber')
network.node('gateway',620,250,360,110,'平台网关侧地址',['172.24.0.1'],parent='platform',kind='teal')
network.node('sink',1120,250,360,110,'平台日志接收端',['172.24.0.1:18100'],parent='platform',kind='teal')
network.node('eth',720,510,360,90,'eth0',['172.24.0.11/24'],parent='container',kind='teal')
network.node('mgmt',410,705,310,110,'环境管理与执行代理',['envd：49983','sandbox-proxy：65225'],parent='container')
network.node('app',775,705,360,110,'终端、API、代理及同步',['65310 / 65213','65216 / 18601'],parent='container')
network.node('ssh',1190,705,260,110,'OpenSSH',['TCP 22'],parent='container')
network.node('loop',410,920,310,125,'容器回环服务',['editor-sdk：39099','同步内部接口：8089'],parent='container')
network.node('docker',775,920,360,125,'内部 Docker 网桥',['docker0：172.17.0.1/16','检查时无运行子容器'],parent='container')
network.node('collector',1190,920,260,125,'日志采集及转发',['目标：网关 TCP 18100'],parent='container',size=17)
network.node('peer',80,550,225,140,'假设：同网段容器',['数量、地址、租户未知','通信需隔离策略允许'],parent='platform',kind='amber',size=16)
network.node('other',80,850,225,145,'假设：其他网络容器',['存在性和地址未知','通信需路由及授权'],parent='platform',kind='amber',size=16)
network.node('egress',600,1310,400,100,'已观察到的公网出口',['43.134.172.85'],kind='teal')
network.node('internet',1110,1310,400,100,'互联网及外部业务服务',['例如腾讯文档等平台依赖'])
network.edge('e-control','control','gateway',[(460,305),(620,305)],kind='amber')
network.edge('e-default','eth','gateway',[(900,510),(900,360)],label=(990,410,'默认路由'))
network.edge('e-management','gateway','mgmt',[(700,360),(700,410),(345,410),(345,675),(565,675),(565,705)],label=(535,410,'已观察：49983 / 65225'))
for id,cx in [('mgmt',565),('app',955),('ssh',1320)]:
    network.edge('e-local-'+id,'eth',id,[(900,600),(900,645),(cx,645),(cx,705)],kind='slate',arrow=False)
network.edge('e-peer','peer','eth',[(305,620),(330,620),(330,555),(720,555)],kind='amber')
network.edge('e-other','other','gateway',[(80,922),(60,922),(60,395),(570,395),(570,305),(620,305)],kind='amber')
network.edge('e-logs','collector','sink',[(1450,982),(1530,982),(1530,305),(1480,305)])
network.edge('e-egress','gateway','egress',[(800,360),(800,380),(335,380),(335,1270),(800,1270),(800,1310)])
network.edge('e-internet','egress','internet',[(1000,1360),(1110,1360)])
network.text('route-note',390,1150,1100,56,['平台网关侧地址可涉及代理或地址转换；无法据此定位原始请求进程。','未扫描其他容器，虚线不代表已验证的可达性。'],18)
network.text('nat-note',50,1440,1500,45,['出口 NAT 的具体层次及公网地址独占性未确认；公网出口地址不等于容器可入站访问的地址。'],18)

namespace = Figure('03-namespace-layers','图 8-1  Namespace 隔离与运行层级',
    '基于容器视角的层级推断｜外层运行时版本与策略需平台确认',1500,1190)
namespace.group('host',440,170,1020,920,'CVM 上层运行环境 · 完整宿主机配置未取得')
namespace.node('cloud',60,240,320,100,'腾讯云基础设施',['DMI 显示 Tencent Cloud / CVM'])
namespace.node('cvm',500,240,900,100,'CVM 虚拟机',['共享 Linux 内核及上层计算、存储资源'],parent='host')
namespace.node('runtime',500,400,900,100,'平台外层容器运行时',['存在 Sysbox 特征；准确版本与创建参数待确认'],parent='host',kind='amber')
namespace.group('container',500,560,900,470,'WorkBuddy 执行容器 · 064f56bb22e3',parent='host',fill='#FFFFFF')
namespace.node('ns',550,625,390,105,'命名空间视图',['user / pid / mnt / net','uts / ipc / cgroup'],parent='container')
namespace.node('cgroup',990,625,360,105,'父级 cgroup 资源限制',['约 4 核 CPU 配额','内存上限 8 GiB'],parent='container',kind='teal')
namespace.node('proc',550,800,390,100,'容器内进程',['docker-init / Supervisor','平台服务及开发任务'],parent='container')
namespace.node('docker',990,800,360,100,'内部容器运行时',['dockerd / containerd'],parent='container')
namespace.node('child',990,950,360,65,'按需创建内部子容器',[],parent='container',kind='amber')
namespace.edge('e-cloud','cloud','cvm',[(380,290),(500,290)])
namespace.edge('e-runtime','cvm','runtime',[(950,340),(950,400)])
namespace.edge('e-container','runtime','container',[(950,500),(950,560)])
namespace.edge('e-ns','ns','proc',[(745,730),(745,800)],kind='slate',arrow=False)
namespace.edge('e-cg','cgroup','proc',[(1170,730),(1170,765),(870,765),(870,800)],kind='slate',arrow=False)
namespace.edge('e-docker','proc','docker',[(940,850),(990,850)],kind='slate',arrow=False)
namespace.edge('e-child','docker','child',[(1170,900),(1170,950)],kind='amber')
namespace.text('side-note',60,410,320,220,['用户映射实测','容器 UID 0 → 外层 UID 100000','','完整 capabilities 受用户','命名空间权限范围约束。'],18)
namespace.text('child-note',550,942,390,70,['检查时无运行的内部子容器。','虚线表示按需创建关系。'],17)
namespace.text('footer',50,1120,1400,45,['命名空间编号与具体隔离证据见第八章；本图不能作为“绝对无法逃逸”的证明。'],18)

resources = Figure('04-resource-inheritance','图 2-1  资源视图与配额继承',
    '规划任务应以可见父级 cgroup 限制为依据｜基于 2026-11-10 检查',1400,1100)
resources.node('visible',340,180,720,110,'系统工具显示的上层资源',['32 个逻辑 CPU / 约 123.32 GiB 内存','可见范围不代表容器独占资源'])
resources.group('budget',60,350,1280,570,'本工作区的资源边界 · 子级无法突破父级限制')
resources.node('parent-limit',340,425,720,120,'可见父级 cgroup',['CPU：400000 / 100000 ≈ 4 核算力配额','内存：8 GiB；进程 / 线程数：151533'],parent='budget',kind='teal')
resources.node('leaf',340,625,720,110,'检查进程所在 init.scope',['CPU、内存、进程数限制显示 max','仍然继承父级上限'],parent='budget')
resources.edge('e-reference','visible','parent-limit',[(700,290),(700,425)],label=(700,323,'实际预算以限制值为准'))
resources.edge('e-inherit','parent-limit','leaf',[(700,545),(700,625)],label=(700,585,'限制沿层级向下生效'))
for id,x,title,kind in [('platform-task',110,'平台服务（示意）','amber'),('user-task',540,'项目任务（示意）','amber'),('docker-task',970,'内部 Docker 任务（示意）','amber')]:
    resources.node(id,x,825,320,65,title,[],parent='budget',kind=kind)
    resources.edge('e-'+id,'leaf',id,[(700,735),(700,780),(x+160,780),(x+160,825)],kind='amber')
resources.text('shared-note',70,950,1260,120,['平台服务、项目进程和内部 Docker 任务共同消耗外层配额；max 不表示无限资源。','任务分组为示意，未逐一核对所有进程及未来子容器的 cgroup 路径。','/dev/shm 的 8 GiB 容量不是额外内存；短时采样也不构成长期性能保证。'],19)

storage = Figure('05-storage-persistence','图 3-1  存储层次与持久化边界',
    '实线表示已观察的路径 / 存储关联；虚线表示待平台确认的恢复能力',1400,1160)
storage.group('observed',40,170,1320,670,'已观察的容器路径与存储结构')
storage.node('paths',120,255,500,110,'工作区与用户文件',['/root / /workspace / /tmp','检查时位于根文件系统视图内'],parent='observed')
storage.node('runtime-paths',780,255,500,110,'内部运行时数据目录',['/var/lib/docker / /var/lib/buildkit','以及 containerd、kubelet 等目录'],parent='observed')
storage.node('overlay',120,470,500,120,'根文件系统：overlay',['可见总容量 256 GiB','采样可用约 253.79 GiB'],parent='observed',kind='teal')
storage.node('runtime-store',780,470,500,120,'运行时目录的后端挂载',['可见平台分配目录及 idmapped 挂载','另见 /dev/nbd962 的 btrfs 后端'],parent='observed',kind='teal')
storage.node('userdata',120,705,500,90,'可写层来源线索',['平台 user-data 路径'],parent='observed')
storage.edge('e-root','paths','overlay',[(370,365),(370,470)])
storage.edge('e-runtime','runtime-paths','runtime-store',[(1030,365),(1030,470)])
storage.edge('e-data','overlay','userdata',[(370,590),(370,705)])
storage.text('scope-note',790,685,490,110,['挂载来源是存储结构线索。','不能据此确定独占容量、数据保留周期，','也不代表相关运行时全部正在运行。'],18)
storage.node('retention',400,940,600,110,'休眠、重建、回收后的数据保留？',['哪些路径受保护、快照周期及恢复时长','均需平台确认，并以恢复演练验收'],kind='amber')
storage.edge('e-retain-left','userdata','retention',[(370,795),(370,880),(700,880),(700,940)],kind='amber')
storage.edge('e-retain-right','runtime-store','retention',[(1030,590),(1320,590),(1320,880),(700,880),(700,940)],kind='amber')
storage.text('bottom',50,1090,1300,40,['文件同步不等于可恢复备份；磁盘设备显示值也不能直接相加为容器可用容量。'],19)

accounts = Figure('06-account-privileges','图 6-1  账号与权限关系',
    '区分密码认证状态、容器内管理权限和外层 UID 映射｜基于 2026-11-10 检查',1400,1100)
accounts.group('container',50,170,1300,640,'容器内部权限范围')
accounts.node('root',100,265,330,110,'root · UID 0',['已设置密码','OpenSSH 配置允许密码认证'],parent='container',size=17)
accounts.node('sudo-users',100,465,330,135,'ubuntu / user',['UID 1000 / 1001','密码锁定；未发现授权公钥'],parent='container',size=17)
accounts.node('admin',600,300,650,130,'容器内 root 管理权限',['可管理容器文件、账号、软件及服务','权限仍受外层隔离约束'],parent='container',kind='teal')
accounts.node('system',600,615,650,125,'其他系统账号',['dockremap / nova / sync：未发现 sudo 权限','另有 21 个禁止登录或不可交互用途账号'],parent='container')
accounts.edge('e-root','root','admin',[(430,320),(600,320)])
accounts.edge('e-sudo','sudo-users','admin',[(430,532),(500,532),(500,390),(600,390)],label=(500,440,'NOPASSWD: ALL'))
accounts.text('sudo-explain',600,465,650,55,['ubuntu / user 不构成可靠的低权限执行边界。'],19)
accounts.text('locked-note',100,650,410,85,['密码锁定限制密码认证，','不等于账号不能被平台进程使用。'],18)
accounts.node('mapping',600,910,650,100,'user namespace 映射',['容器 UID 0 → 直接外层 UID 100000','不能由此获得外层 UID 0 的权限'],kind='teal')
accounts.edge('e-map','admin','mapping',[(1250,365),(1320,365),(1320,860),(925,860),(925,910)],label=(1100,860,'映射关系，不是登录或提权路径'))
accounts.text('bottom',60,1040,1280,40,['建议执行项目代码时使用无免密码 sudo、无不必要 capabilities 和管理 socket 权限的独立账号。'],18)

ssh_access = Figure('07-ssh-access-conditions','图 7-2  OpenSSH 访问条件',
    '箭头表示条件检查顺序，不代表已完成连接或密码认证测试',1400,1300)
ssh_access.node('request',340,180,720,85,'候选连接',['连接目标：容器 OpenSSH TCP 22'])
ssh_access.group('outer',60,330,1280,160,'平台外层 · 需要平台核验')
ssh_access.node('outer-policy',340,385,720,85,'安全组、路由、端口发布及网络策略是否允许？',['外层规则未取得，实际来源范围未知'],parent='outer',kind='amber',size=18)
ssh_access.group('inner',60,545,1280,620,'容器内部 · 已核对配置')
ssh_access.node('listener',340,615,720,115,'监听与已检查的 INPUT 规则',['监听 0.0.0.0:22、[::]:22','已检查的 IPv4 / IPv6 INPUT 链无来源限制'],parent='inner')
ssh_access.node('auth',340,815,720,135,'OpenSSH 认证及账号条件',['root 密码认证允许；空密码禁止','还需有效凭据、账号状态、Shell 与 PAM 条件满足'],parent='inner')
ssh_access.node('session',340,1040,720,90,'所有条件满足后才能建立会话',['实际密码登录及密码强度未验证'],parent='inner',kind='amber')
ssh_access.edge('e-outer','request','outer-policy',[(700,265),(700,385)])
ssh_access.edge('e-network','outer-policy','listener',[(700,470),(700,615)])
ssh_access.edge('e-auth','listener','auth',[(700,730),(700,815)])
ssh_access.edge('e-session','auth','session',[(700,950),(700,1040)])
ssh_access.text('bottom',60,1210,1280,60,['任一条件不满足，均可能阻止会话建立；仅凭通配地址监听或容器 INPUT 为 ACCEPT，','不能认定公网可达，也不能把访问范围归结为某个已确认的网段。'],19)

logs = Figure('08-log-audit-chain','图 11-1  日志链路与审计缺口',
    '蓝色实线表示已观察的采集 / 发送链路线索；橙色虚线表示尚待确认的环节',1500,1170)
logs.group('container',50,180,900,650,'WorkBuddy 容器内部')
logs.group('platform',1010,180,440,650,'平台侧')
logs.node('stdout',100,265,360,100,'部分服务标准输出',['并非所有服务均已确认覆盖'],parent='container')
logs.node('tee',550,265,340,100,'log-forward-tee',['复制及转发输出'],parent='container')
logs.node('files',100,455,360,100,'平台日志文件',['采集目录与覆盖范围需复核'],parent='container')
logs.node('collector',550,455,340,100,'sandbox-log-collector',['已观察到采集进程运行'],parent='container')
logs.node('sshd',100,650,360,110,'OpenSSH 认证事件',['登录成功 / 失败及相关行为'],parent='container')
logs.node('gap',550,650,340,110,'留存链路未确认',['常规 auth.log / journal 缺失','sshd 标准输出指向空设备'],parent='container',kind='amber',size=17)
logs.node('sink',1060,350,340,160,'平台日志接收端',['172.24.0.1:18100','已观察到多个连接'],parent='platform',kind='teal')
logs.node('backend',1060,620,340,135,'平台日志后台',['是否完整入库、可检索','以及保留期限均未验证'],parent='platform',kind='amber',size=18)
logs.edge('e-tee','stdout','tee',[(460,315),(550,315)])
logs.edge('e-collector','files','collector',[(460,505),(550,505)])
logs.edge('e-sink1','tee','sink',[(890,315),(980,315),(980,415),(1060,415)])
logs.edge('e-sink2','collector','sink',[(890,505),(980,505),(980,460),(1060,460)])
logs.edge('e-backend','sink','backend',[(1230,510),(1230,620)],kind='amber')
logs.edge('e-gap','sshd','gap',[(460,705),(550,705)],kind='amber')
logs.node('verify',300,940,900,115,'建议补齐并验收的审计事件',['登录成功 / 失败、权限变更、服务异常退出、OOM 与关键操作','确认覆盖范围、检索方式、保留期限和导出能力'],kind='amber')
logs.edge('e-verify','gap','verify',[(720,760),(720,940)],kind='amber',label=(720,875,'待平台核验与补齐'))
logs.text('bottom',60,1095,1380,40,['存在日志发送连接不等于日志已完整入库；本地日志缺失也不能单独证明平台没有另行采集。'],19)

FIGURES=[resources,storage,service,accounts,network,ssh_access,namespace,logs]


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
    for kind in ['blue','amber','slate']:
        p.append(f'<marker id="arrow-{kind}" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M 0 1 L 8 5 L 0 9 Z" fill="{C[kind]}"/></marker>')
    p += ['</defs>',f'<rect width="{fig.w}" height="{fig.h}" fill="white"/>',
          '<g font-family="Noto Sans CJK SC, Microsoft YaHei, sans-serif">',
          f'<rect x="40" y="42" width="7" height="38" rx="3" fill="{C["teal"]}"/>',
          text_svg([fig.title],64,75,34,C['ink'],'start',True),
          text_svg([fig.subtitle],64,109,18,C['muted'],'start')]
    for n in fig.groups:
        p.append(f'<rect x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" rx="18" fill="{n["fill"]}" stroke="{C["line"]}" stroke-width="1.5"/>')
        p.append(text_svg([n['title']],n['x']+24,n['y']+37,22,C['ink'],'start',True))
    for e in fig.edges:
        pts=' '.join(f'{x},{y}' for x,y in e['points'])
        dash=' stroke-dasharray="8 6"' if e['kind']=='amber' else ''
        marker=f' marker-end="url(#arrow-{e["kind"]})"' if e['arrow'] else ''
        p.append(f'<polyline points="{pts}" fill="none" stroke="{C[e["kind"]]}" stroke-width="2.3" stroke-linejoin="round"{dash}{marker}/>')
    for n in fig.nodes:
        fill,stroke=colors(n['kind'])
        dash=' stroke-dasharray="8 6"' if n['kind']=='amber' else ''
        p.append(f'<rect x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="1.6"{dash}/>')
        title_size=21 if n['w']>250 else 19
        block=title_size+len(n['body'])*(n['size']*1.45)+ (9 if n['body'] else 0)
        baseline=n['y']+(n['h']-block)/2+title_size*.87
        assert font_width(n['title'],title_size)<n['w']-24,(fig.key,n['title'])
        p.append(text_svg([n['title']],n['x']+n['w']/2,baseline,title_size,C['ink'],bold=True))
        for j,line in enumerate(n['body']):
            assert font_width(line,n['size'])<n['w']-22,(fig.key,line)
            p.append(text_svg([line],n['x']+n['w']/2,baseline+12+(j+1)*n['size']*1.45,n['size'],C['muted']))
    for e in fig.edges:
        if e['label']:
            x,y,label=e['label'];w=font_width(label,17)+20
            p.append(f'<rect x="{x-w/2}" y="{y-15}" width="{w}" height="28" rx="5" fill="white"/>')
            p.append(text_svg([label],x,y+5,17,C['blue']))
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
    textcell('subtitle',64,85,fig.w-100,30,[fig.subtitle],18,C['muted'])
    vertex('accent','',f'rounded=1;fillColor={C["teal"]};strokeColor=none;',40,42,7,38)
    for n in fig.groups:
        style=f'rounded=1;arcSize=8;whiteSpace=wrap;html=1;fillColor={n["fill"]};strokeColor={C["line"]};strokeWidth=1.5;align=left;verticalAlign=top;spacingLeft=24;spacingTop=16;fontFamily=Noto Sans CJK SC;fontSize=22;fontStyle=1;fontColor={C["ink"]};container=1;collapsible=0;recursiveResize=0;'
        vertex(n['id'],escape(n['title']),style,n['x'],n['y'],n['w'],n['h'],n['parent'])
    for n in fig.nodes:
        fill,stroke=colors(n['kind']);ts=21 if n['w']>250 else 19
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
            x,y,label=e['label'];w=font_width(label,17)+20
            vertex(e['id']+'-label',escape(label),f'text;html=1;fillColor=#FFFFFF;strokeColor=none;align=center;verticalAlign=middle;fontFamily=Noto Sans CJK SC;fontSize=17;fontColor={C["blue"]};',x-w/2,y-15,w,28)
    for t in fig.texts:textcell(t['id'],t['x'],t['y'],t['w'],t['h'],t['lines'],t['size'],t['color'],t['bold'],t['align'])
    return model


def drawio(figures,path):
    doc=ET.Element('mxfile',host='app.diagrams.net',type='device',version='24.7.17')
    for f in figures:
        d=ET.SubElement(doc,'diagram',id=f.key,name=f.title)
        d.append(mxmodel(f))
    ET.indent(doc,space='  ')
    ET.ElementTree(doc).write(path,encoding='utf-8',xml_declaration=True)


for f in FIGURES:
    path=OUT/(f.key+'.svg');path.write_text(svg(f),encoding='utf-8')
    drawio([f],OUT/(f.key+'.drawio'))
    subprocess.run(['rsvg-convert','--width',str(f.w*2),'--height',str(f.h*2),'-o',str(OUT/(f.key+'.png')),str(path)],check=True)
    with Image.open(OUT/(f.key+'.png')) as im:
        im.thumbnail((1200,1200))
        im.convert('RGB').save(BASE/'diagram_sources'/(f.key+'-preview.jpg'),quality=92)
drawio(FIGURES,OUT/'完整报告图集.drawio')

original=REPORT.read_text(encoding='utf-8')
backup=BASE/'diagram_sources'/'report-before-extra-diagrams.md'
if not backup.exists():backup.write_text(original,encoding='utf-8')
text=original
tree=r'```text\ndocker-init\n└─ supervisord\n.*?```'
def embed(f):
    folder='assets/report-diagrams/'
    return f'![{f.title}]({folder}{f.key}.png)\n\n[SVG 矢量图]({folder}{f.key}.svg) · [可编辑 draw.io 源文件]({folder}{f.key}.drawio)'
text,n=re.subn(tree,lambda _:embed(service),text,count=1,flags=re.S)
assert n in [0,1]
it=iter([network,namespace])
text,n=re.subn(r'```mermaid\n.*?```',lambda _:embed(next(it)),text,flags=re.S)
assert n in [0,2]
for f in [service,network,namespace]:
    pattern=r'!\[[^\]]*\]\(assets/report-diagrams/'+re.escape(f.key)+r'\.png\)\n\n\[SVG 矢量图\][^\n]+'
    text,n=re.subn(pattern,lambda _:embed(f),text)
    assert n==1,(f.key,n)
additions=[
    (resources,'### 2.3 检查时的资源健康状态','下图说明上层资源视图、父级配额与子任务之间的关系。平台服务和项目任务共同消耗外层预算；任务分组为示意，不表示所有进程或未来子容器均属于同一个子 cgroup。'),
    (storage,'## 第四章　操作系统与软件环境','下图将可观察的存储结构与尚未验证的数据保留能力分开。虚线表示需要平台确认的持久化和恢复保障，不表示已建立备份。'),
    (accounts,'### 6.3 其他系统账号','下图区分账号认证状态、容器内权限和用户命名空间映射。免密码 sudo 会使普通账号具备获取容器 root 权限的途径，但不意味着获得外层宿主机 root 权限。'),
    (ssh_access,'## 第八章　Namespace 隔离与运行层级','下图按逻辑顺序整理建立 OpenSSH 会话所需的条件。它描述配置和依赖关系，不表示已完成公网连通性或实际密码认证测试。'),
    (logs,'### 11.2 本地认证与审计日志缺口','下图区分已观察到的日志发送链路，以及尚未确认的认证日志留存和平台后台处理环节。连接存在不能替代日志覆盖与留存验证。'),
]
for f,anchor,intro in additions:
    block=f'<!-- diagram:{f.key} -->\n\n{intro}\n\n{embed(f)}\n\n<!-- /diagram:{f.key} -->'
    pattern=r'<!-- diagram:'+re.escape(f.key)+r' -->.*?<!-- /diagram:'+re.escape(f.key)+r' -->'
    if re.search(pattern,text,flags=re.S):
        text=re.sub(pattern,lambda _:block,text,flags=re.S)
    else:
        assert text.count(anchor)==1,anchor
        # Keep chapter separators immediately before their chapter heading.
        target=('---\n\n'+anchor) if anchor.startswith('## ') else anchor
        assert target in text
        text=text.replace(target,block+'\n\n'+target,1)
insert='**图件附件：** [完整可编辑图集（draw.io，8 页）](assets/report-diagrams/完整报告图集.drawio)。正文使用 PNG 直接展示，每图另附 SVG 与独立 draw.io 源文件。图件按章节编号，于 2026 年 11 月 15 日重新绘制并补充；检查数据日期保持不变。'
if re.search(r'^\*\*图件附件：\*\*.*$',text,re.M):
    text=re.sub(r'^\*\*图件附件：\*\*.*$',lambda _:insert,text,flags=re.M)
else:
    text=text.replace('\n---\n','\n'+insert+'\n\n---\n',1)
REPORT.write_text(text,encoding='utf-8')

manifest=[]
for f in FIGURES:
    manifest.append({'figure':f.title,'size':[f.w,f.h],'png_size':[f.w*2,f.h*2],'nodes':len(f.nodes),'groups':len(f.groups),'edges':len(f.edges),'files':[f.key+s for s in ['.svg','.png','.drawio']]})
(BASE/'diagram_sources'/'diagram-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')

archive=BASE/'腾讯云CVM-Linux容器开发环境综合检查报告-图文及可编辑源文件.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
    z.write(REPORT,REPORT.name)
    for p in sorted(OUT.iterdir()):
        if p.suffix in ['.svg','.png','.drawio']:z.write(p,p.relative_to(BASE))
print(json.dumps({'report':str(REPORT),'archive':str(archive),'figures':manifest},ensure_ascii=False,indent=2))
