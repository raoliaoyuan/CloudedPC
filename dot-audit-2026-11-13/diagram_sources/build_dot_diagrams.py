from pathlib import Path
import json, subprocess
from PIL import Image
from diagram_engine import Figure, svg, drawio

BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'assets/report-diagrams'
OUT.mkdir(parents=True,exist_ok=True)
FIGURES=[]
META=[]

def finish(f,chapter,caption,sources):
    FIGURES.append(f)
    META.append(dict(key=f.key,title=f.title,chapter=chapter,caption=caption,sources=sources,width=f.w,height=f.h))

f=Figure('01-environment-boundaries','图 1-1  产品能力与执行环境边界',
 '产品逻辑关系，非物理部署拓扑｜青色：官方说明；橙色虚线：未确认',1400,1040)
f.node('dot',440,175,520,115,'Dot 代理〔官方〕',['接收任务并协调执行环境'],kind='teal')
f.node('own',55,400,400,180,'自有云电脑〔官方〕',['有自己的文件与浏览器会话','可供研究、文档与软件工作'],kind='teal',size=24)
f.node('connected',500,400,400,180,'连接的用户电脑〔官方〕',['需连接授权与设备在线','不是自有云电脑的同一工作区'],kind='teal',size=24)
f.node('codex',945,400,400,180,'Codex 云任务〔官方〕',['可使用准备好的仓库环境','不能据此认定与桌面同镜像'],kind='teal',size=24)
f.edge('own-link','dot','own',[(570,290),(570,345),(255,345),(255,400)],kind='teal')
f.edge('connected-link','dot','connected',[(700,290),(700,400)],kind='teal')
f.edge('codex-link','dot','codex',[(830,290),(830,345),(1145,345),(1145,400)],kind='teal')
f.text('scope',70,620,1260,75,['箭头表示官方产品能力；不表示本账号已启用全部连接，亦不表示三个独立物理服务器。'],24)
f.node('unknown',180,745,1040,150,'本实例的具体部署尚未确认',['供应商、区域、VM 数量、容器运行时、宿主与网络隔离层次','不能由 overlay、私有地址或 CPU 型号推定 Docker / Kubernetes'],kind='amber',size=25)
f.text('source',60,950,1280,60,['来源：[O1][O4] 产品关系；[O2][O3] 共同基础设施说明；[A #021、#024、#027] 记录。'],22)
finish(f,1,'图示区分产品能力与本实例部署事实。共用基础设施的官方说明不足以确定本实例的虚拟机、容器或网络命名空间数量；各分支也不表示本账号已连接或正在执行。','[O1][O2][O3][O4][A：#021、#024、#027]')

f=Figure('02-resource-limits','图 2-1  可见资源与实际配额核验',
 '蓝色：历史助手记录；橙色虚线：缺失证据；灰色：通用技术解释',1400,1120)
f.node('cpu',70,190,600,170,'CPU 可见值〔记录〕',['AMD EPYC 9V74 型号字符串','9 个逻辑 CPU；允许 CPU 0–8'],size=27)
f.node('memory',730,190,600,170,'内存可见值〔记录〕',['总量约 9.73 GiB','当时已用 1.64 GiB；可用 8.09 GiB'],size=27)
f.node('cpu-limit',70,485,600,170,'CPU 实际限制〔未确认〕',['缺少 cpu.max 与可读父层限制','也未完成独占性与持续性能验证'],kind='amber',size=26)
f.node('memory-limit',730,485,600,170,'内存硬限制〔未确认〕',['缺少 memory.max 与可读父层限制','可见总量不自动等于允许使用上限'],kind='amber',size=26)
f.edge('cpu-check','cpu','cpu-limit',[(370,360),(370,485)],kind='amber',label=(370,420,'需补证据，不能直接换算'))
f.edge('mem-check','memory','memory-limit',[(1030,360),(1030,485)],kind='amber',label=(1030,420,'需补证据，不能直接等同'))
f.group('technical',70,765,1260,215,'通用 cgroup v2 机制〔技术说明，不是 Dot 已测配置〕')
f.text('rule',110,830,1180,120,['CPU 时间上限 = quota / period；子级仍受父级限制。','内存须核对硬限制；若采用其他资源控制机制，应按实际实现核验。','没有原始限制与基准测试，不能认定“独占 9 核 / 10 GiB”。'],26)
f.text('source',60,1030,1280,55,['来源：[A #024]；[T1] Linux cgroup v2。模型推理硬件也不能由此 CPU 视图反推。'],23)
finish(f,2,'上半部分是附件中的可见值，下半部分是仍待取得的限制与解释规则。虚线表示需要核验的关系，不代表已经查到隐藏配额。','[A：#024][T1]')

f=Figure('03-storage-evidence','图 3-1  存储视图与容量统计疑点',
 '蓝色：记录值；橙色虚线：待解释或未确认；计算结果只用于核对口径',1400,1180)
f.node('overlay',330,175,740,110,'工作区文件系统 overlay〔记录〕',['不能据此确定底层物理盘或容器产品'],size=26)
f.node('capacity',70,390,600,160,'总量与可用量〔记录〕',['总量约 62.94 GiB','可用约 59.54 GiB'],size=28)
f.node('used',730,390,600,160,'已用量〔记录〕',['约 195 MiB；约 1%','未取得同一时刻的原始字节数'],size=28)
f.edge('view1','overlay','capacity',[(560,285),(560,335),(370,335),(370,390)],kind='slate',arrow=False)
f.edge('view2','overlay','used',[(840,285),(840,335),(1030,335),(1030,390)],kind='slate',arrow=False)
f.node('difference',250,665,900,170,'差额口径待解释〔复核计算〕',['62.94 − 59.54 = 3.40 GiB，约 3,482 MiB','与“已用 195 MiB”不能直接对齐','保留空间、统计字段或上下文差异均只是候选解释'],kind='amber',size=25)
f.edge('calc1','capacity','difference',[(370,550),(370,610),(530,610),(530,665)],kind='amber')
f.edge('calc2','used','difference',[(1030,550),(1030,610),(870,610),(870,665)],kind='amber')
f.text('tmpfs',70,900,1260,90,['tmpfs 的各约 4.87 GiB 是上限，不可相加为额外 RAM。','SSD / NVMe、IOPS、独享容量与数据保留承诺均未确认。'],27)
f.text('source',60,1080,1280,60,['来源：[A #024]；[T2] OverlayFS；[T3] tmpfs。此差异不等于磁盘损坏或记录造假。'],23)
finish(f,3,'容量差额来自原报告的算术复核，图中未将差额归因为特定保留分区。overlay 和 tmpfs 的名称也不能用来认定磁盘介质、额外内存或持久化期限。','[A：#024][T2][T3]')

f=Figure('04-network-contexts','图 4-1  三种联网上下文与代理路径',
 '蓝色实线：记录中的配置或操作；橙色虚线：链路细节未确认；非抓包拓扑',1400,1240)
for key,x,title,body in [
 ('browser',55,'云端 Chromium〔记录〕',['启动参数由历史助手转述']),
 ('terminal',500,'桌面终端〔用户记录〕',['用户称请求失败']),
 ('tool',945,'助手命令工具〔记录〕',['助手称单个请求成功'])]:
 f.node(key,x,190,400,130,title,body,size=24)
f.node('browser-proxy',55,455,400,150,'显式 HTTP 代理〔记录〕',['browser-proxy:8889','具体逐请求路径未取证'],size=25)
f.node('terminal-config',500,455,400,150,'程序网络配置〔未确认〕',['实际代理、DNS、证书','执行上下文与错误码'],kind='amber',size=25)
f.node('loopback-proxy',945,455,400,150,'本地临时代理〔记录〕',['127.0.0.1:临时端口','不能把早期端口直接套入'],size=25)
f.edge('browser-config','browser','browser-proxy',[(255,320),(255,455)],label=(255,388,'配置线索'))
f.edge('terminal-config-link','terminal','terminal-config',[(700,320),(700,455)],kind='amber')
f.edge('tool-config','tool','loopback-proxy',[(1145,320),(1145,455)],label=(1145,388,'助手报告的操作'))
f.node('website',55,760,400,140,'目标网站〔逻辑终点〕',['出口及后续代理链未知'],kind='amber',size=25)
f.node('terminal-result',500,760,400,140,'请求结果待复现',['不能据此认定全部断网'],kind='amber',size=25)
f.node('chatgpt',945,760,400,140,'chatgpt.com〔记录〕',['助手称返回 HTTP 200','只支持当时该目标的陈述'],size=25)
f.edge('browser-remote','browser-proxy','website',[(255,605),(255,760)],kind='amber',label=(255,680,'后续链路未确认'))
f.edge('terminal-remote','terminal-config','terminal-result',[(700,605),(700,760)],kind='amber')
f.edge('tool-remote','loopback-proxy','chatgpt',[(1145,605),(1145,760)],kind='amber',label=(1145,680,'后续链路未确认'))
f.text('meaning',70,970,1260,115,['主机名映射不等于网卡绑定；三个上下文不等于三个已确认容器。','浏览器出站代理不是已确认的 GUI 画面传输通道。','GUI 协议、出口 IP、TLS 检查范围与完整网络空间关系均未确认。'],26)
f.text('source',60,1160,1280,45,['来源：[A #021、#025、#027、#036]；[O2] 分项控制；[T4][T5][T6] 技术解释。'],22)
finish(f,4,'图中保留三种访问上下文，实线仅代表历史记录中的配置或操作陈述，不能当作抓包确认。未画出具体容器、网卡或公网出口；浏览器代理与 GUI 画面链路也没有被合并。','[A：#021、#025、#027、#036][O2][T4][T5][T6]')

f=Figure('05-preview-and-access','图 6-1  本地预览与外部访问边界',
 '蓝色：助手记录；青色：用户结果确认；橙色虚线：未验收的外部访问',1400,1160)
f.group('cloud',55,175,1290,390,'Dot 云电脑中的开发与预览〔逻辑范围，不确定具体进程拓扑〕')
f.node('app',100,300,480,165,'数独 Web 服务〔记录〕',['助手称已启动并打包','自动测试通过仍缺原始日志'],parent='cloud',size=26)
f.node('preview',820,300,480,165,'云端预览〔用户确认〕',['用户 #060 表示可以正常玩','支持当时的结果可用性'],parent='cloud',kind='teal',size=26)
f.edge('preview-link','preview','app',[(820,382),(580,382)],label=(700,340,'预览访问'))
f.node('user-pc',70,705,580,170,'用户自己的电脑',['本机 localhost 指向本机上下文','不是 Dot 中同名地址的自动映射'],size=26)
f.node('external',750,705,580,170,'外部访问入口〔未确认〕',['公网 IP、入站端口与服务授权','独立 SSH、Tailscale 及持续在线'],kind='amber',size=26)
f.edge('external-test','user-pc','external',[(650,790),(750,790)],kind='amber')
f.edge('inbound','external','app',[(1040,705),(1040,625),(340,625),(340,465)],kind='amber',label=(700,625,'需分别验收外部入口及目标服务'))
f.text('tailscale',70,950,1260,90,['没有 TUN 不足以排除 Tailscale 用户态模式；但本例没有上线或对端连通验收。','本地预览成功不能替代公网发布验收；Sites 发布能力也不证明 Dot 入站端口开放。'],25)
f.text('source',60,1080,1280,45,['来源：[A #012—#018、#048、#060、#064]；[T4][T9]；[O6]。'],23)
finish(f,6,'将已经有用户结果确认的本地预览，与尚未验收的公网、SSH 和尾网访问分开。虚线表示待验证能力，不代表已建立路由，也不表示平台永久禁止这些功能。','[A：#012—#018、#048、#060、#064][T4][T9][O6]')

f=Figure('06-permission-controls','图 7-1  权限控制与实例证据边界',
 '青色：官方控制项；蓝色：历史助手陈述；橙色虚线：缺少本实例证据',1400,1160)
f.node('owner',350,175,700,115,'拥有者授权与适用工作区规则〔官方〕',['连接的账号权限与动作限制共同约束任务'],kind='teal',size=26)
for key,x,title,body in [
 ('browse',55,'浏览器访问',['网站访问与已登录账号范围']),
 ('shell',500,'代码与 Shell 联网',['代码发起的网络访问']),
 ('desktop',945,'桌面交互',['查看与交互能力'])]:
 f.node(key,x,410,400,140,title+'〔官方〕',body,kind='teal',size=24)
 f.edge('rule-'+key,'owner',key,[(700,290),(700,350),(x+200,350),(x+200,410)],kind='teal')
f.node('review',180,655,1040,120,'需要审查的动作适用 Auto-review〔官方〕',['此框表示动作审查机制，不是网络代理或某个已确认的本地进程'],kind='teal',size=25)
f.node('reported',70,875,580,150,'助手报告的限制〔记录〕',['称没有管理员权限和 TUN','不足以证明所有进程均非 root'],size=26)
f.node('unknown',750,875,580,150,'本实例仍缺少〔未确认〕',['id、capabilities、seccomp','SSH、防火墙与完整策略证据'],kind='amber',size=26)
f.text('source',60,1080,1280,50,['来源：[O2]；[A #012、#021、#024]。控制项彼此独立，不能由一个入口推定其他入口。'],22)
finish(f,7,'图中分开的官方控制项不是三个已确认的安全设备。Auto-review 是机制说明；附件中的权限受限陈述不足以替代用户身份、capabilities、seccomp 或策略审计。','[O2][A：#012、#021、#024]')

f=Figure('07-persistence-lifecycle','图 8-1  状态保留与持续运行的区别',
 '青色：官方能力；橙色虚线：本实例仍需核验；箭头为状态逻辑，不是时间 SLA',1400,1190)
f.node('working',70,185,580,150,'使用时段 A〔官方能力〕',['云电脑具有自己的文件','软件与浏览器会话'],kind='teal',size=27)
f.node('later',750,185,580,150,'后续使用时段 B〔官方能力〕',['可跨使用时段保留状态','安全文档说明跨会话快照'],kind='teal',size=27)
f.edge('continuity','working','later',[(650,260),(750,260)],kind='teal')
f.group('objects',70,440,1260,360,'必须分别核验的对象〔支持保留状态，不代表以下项目全有相同保证〕')
for key,x,title,body in [
 ('files',100,'文件与目录',['具体路径、保留期限','恢复后哈希是否一致']),
 ('cookies',525,'浏览器登录态',['可能受网站会话失效影响','与文件快照不是同一对象']),
 ('process',950,'进程与网络连接',['进程、监听端口、TCP 会话','是否继续或恢复仍未知'])]:
 f.node(key,x,535,350,200,title,body,parent='objects',kind='amber',size=23)
f.node('policy',70,915,600,145,'适用账号策略〔未确认〕',['企业条件化保留规则不能直接套用','不能承诺统一文件寿命或永久保存'],kind='amber',size=25)
f.node('backup',730,915,600,145,'独立副本与恢复演练〔建议〕',['源码和交付物保留独立副本','恢复成功仅证明该次情景'],kind='amber',size=26)
f.text('source',60,1125,1280,45,['来源：[O1][O2]；[A #039、#042]。状态延续不等于任意后台服务不间断运行。'],23)
finish(f,8,'文件、浏览器会话、进程与连接需要分别验收。官方支持状态延续，但本例账号的具体保留规则、进程恢复和长期服务保障尚未核实；图中不绘制已建立的备份链路。','[O1][O2][A：#039、#042]')

f=Figure('08-human-takeover','图 8-2  云电脑查看与人工接管流程',
 '青色：官方操作流程；橙色虚线：实现与体验原因未确认；非内部设计披露',1400,1200)
steps=[('open',170,'打开云电脑',['进入查看界面']),('take',380,'Take over',['取得鼠标与键盘控制']),('act',590,'人工完成操作',['例如网站登录或额外验证']),('return',800,'Return control',['将控制交还 Dot'])]
for key,y,title,body in steps:
 f.node(key,90,y,660,115,title,body,kind='teal',size=28)
for (a,y,*_),(b,ny,*_) in zip(steps,steps[1:]):
 f.edge(a+'-'+b,a,b,[(420,y+115),(420,ny)],kind='teal')
f.node('view-note',865,170,445,135,'查看不等于已接管',['打开画面后仍需选择 Take over'],kind='teal',size=23)
f.node('continue',865,800,445,115,'Dot 继续任务',['控制权交接后的工作延续'],kind='teal',size=25)
f.edge('continue-link','return','continue',[(750,857),(865,857)],kind='teal')
f.node('unknown',865,420,445,220,'尚未确认的实现',['GUI 传输协议与桌面组件','编码、帧率、输入转发机制','界面简化的内部设计动机'],kind='amber',size=24)
f.text('boundary',70,995,1260,85,['流程能够解释“查看、接管、交还”的关系，不能解释或证明界面难用的根因。','没有证据说明简陋 GUI 是安全、成本或代理工作的必要代价。'],26)
f.text('source',60,1130,1280,40,['来源：[O1] Use the cloud computer / Sign in to a website；未确认项沿用正文证据边界。'],22)
finish(f,8,'官方明确提供人工接管与交还控制流程。图示补充操作关系，不构成 GUI 性能实测，也不把产品工作方式写成简陋界面的已确认设计动机。','[O1]')

for f in FIGURES:
    p=OUT/(f.key+'.svg');p.write_text(svg(f))
    drawio([f],OUT/(f.key+'.drawio'))
    subprocess.run(['/usr/bin/rsvg-convert','--width',str(f.w*2),'--height',str(f.h*2),'-o',str(OUT/(f.key+'.png')),str(p)],check=True)
    with Image.open(OUT/(f.key+'.png')) as im:
        im.thumbnail((1400,1400));im.convert('RGB').save(BASE/'diagram_sources'/(f.key+'-preview.jpg'),quality=94)
drawio(FIGURES,OUT/'Dot云电脑完整图集.drawio')
(BASE/'diagram_sources/diagram-manifest.json').write_text(json.dumps(META,ensure_ascii=False,indent=2))
print(json.dumps({'figures':len(FIGURES),'assets':str(OUT),'diagram_pages':[f.title for f in FIGURES]},ensure_ascii=False,indent=2))
