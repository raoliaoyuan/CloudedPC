from pathlib import Path
import subprocess, json
from PIL import Image
from diagram_engine import Figure, svg, drawio

BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'assets/report-diagrams'
OUT.mkdir(parents=True,exist_ok=True)
FIGURES=[]
META=[]
def finish(f,caption,sources):
    FIGURES.append(f)
    META.append(dict(key=f.key,title=f.title,caption=caption,sources=sources,width=f.w,height=f.h))

f=Figure('01-comparison-scope','图 1  比较对象与证据边界','逻辑范围图｜蓝色：历史资料，等级见框内；青色：官方；橙色虚线：未确认',1400,1050)
f.group('dot',50,175,620,660,'Codex Dot 云电脑')
f.group('wb',730,175,620,660,'WorkBuddy 云 PC 本实例')
f.node('dot-official',85,265,550,150,'任务与云电脑〔官方〕',['Dot 有自有云电脑与浏览器','可委派任务并由用户必要时接管'],parent='dot',kind='teal',size=26)
f.node('dot-evidence',85,465,550,145,'实例证据〔记录与观察〕',['配置多为历史助手陈述','数独可玩与 GUI 操作有用户确认'],parent='dot',size=26)
f.node('dot-unknown',85,660,550,125,'部署细节〔未确认〕',['运行时、配额、底层拓扑'],parent='dot',kind='amber',size=26)
f.node('wb-evidence',765,265,550,150,'Tencent Cloud CVM〔实测线索〕',['DMI 厂商与产品标识','当前工作区是 Linux 容器'],parent='wb',size=26)
f.node('wb-service',765,465,550,145,'容器内管理〔历史实测〕',['终端、CodeBuddy 与 Docker 组件','有配置、进程和访问证据'],parent='wb',size=26)
f.node('wb-boundary',765,660,550,125,'宿主能力〔未确认〕',['Sysbox 特征是推断；无宿主管理权'],parent='wb',kind='amber',size=24)
f.text('rules',70,880,1260,95,['Dot 自有云电脑、委派的 Codex Cloud 与连接的个人电脑不能混为同一环境。','两边都涉及代理工具；本图不比较代理模型质量，也不把单个实例泛化为产品规格。'],25)
f.text('source',60,990,1280,40,['来源：[W1 第 2、5、8 章][A #024、#060][U1][O1][O3]。'],22)
finish(f,'两列表示本报告的比较范围。相近名称、共同使用代理或都能执行代码，不证明执行环境、权限和交互方式相同。','[W1][A][U1][O1][O3]')

f=Figure('02-resource-comparison','图 2  可见资源与实际限制','蓝色：历史实测或记录；橙色虚线：需补证据；同口径后才能比较',1400,1080)
f.node('dot-view',70,190,600,160,'Dot 可见视图〔记录〕',['9 个逻辑 CPU','内存总量约 9.73 GiB'],size=28)
f.node('wb-view',730,190,600,160,'WorkBuddy 可见视图〔实测〕',['32 个逻辑 CPU','内存总量约 123.32 GiB'],size=28)
f.node('dot-limit',70,500,600,165,'实际限制〔未确认〕',['缺少 cpu.max、memory.max','或其他资源控制机制的原始证据'],kind='amber',size=26)
f.node('wb-limit',730,500,600,165,'父级限制〔历史实测〕',['400000 / 100000 → 4 核时间上限','memory.max → 8 GiB 硬限制'],size=26)
f.edge('dot-check','dot-view','dot-limit',[(370,350),(370,500)],kind='amber',label=(370,425,'不能直接当成配额'))
f.edge('wb-check','wb-view','wb-limit',[(1030,350),(1030,500)],label=(1030,425,'实际核对父级约束'))
f.node('conclusion',140,800,1120,145,'比较结论〔技术分析〕',['9 个可见 CPU 与 4 核时间上限不是同一种指标','没有同负载基准，不能据此排名性能、独占性或响应速度'],kind='slate',size=27)
f.text('source',60,1000,1280,50,['来源：[A #024][W1 第 2 章][T1]。4 核上限不是 4 个独占物理核，也不是保底性能。'],22)
finish(f,'WorkBuddy 已取得父级限制，Dot 仍缺对应证据。虚线表示待核验，不能填入猜测配额；存储容量也应与性能和持久性分开。','[A：#024][W1：第 2、3 章][T1]')

f=Figure('03-network-comparison','图 3  远程入口与网络证据','箭头表示已支持的逻辑访问关系，不是完整抓包拓扑',1400,1180)
f.group('wb',50,170,620,740,'WorkBuddy 本实例')
f.group('dot',730,170,620,740,'Codex Dot 云电脑')
f.node('wb-user',90,260,540,110,'用户端发起远程访问',['历史 SSH 登录成功'],parent='wb',size=26)
f.node('wb-entry',90,450,540,145,'Tailscale 入口〔历史实测〕',['用户态模式在线','此处不等同于容器 OpenSSH'],parent='wb',size=25)
f.node('wb-target',90,660,540,115,'WorkBuddy 执行环境',['可开展已授权的终端管理'],parent='wb',size=26)
f.edge('wb1','wb-user','wb-entry',[(360,370),(360,450)])
f.edge('wb2','wb-entry','wb-target',[(360,595),(360,660)])
f.text('wb-note',95,810,530,70,['独立探测经 DERP(sin)，均值 104.6 ms','不是该次 SSH 的完整抓包或 GUI 测量'],22)
f.node('dot-user',770,260,540,110,'用户操作 GUI〔用户观察〕',['可操作，但反馈体验差'],parent='dot',size=26)
f.node('dot-entry',770,450,540,145,'人工接管〔官方〕',['查看后选择 Take over','GUI 协议与传输路径未确认'],parent='dot',kind='teal',size=25)
f.node('dot-target',770,660,540,115,'Dot 云电脑',['用户确认数独本地预览可玩'],parent='dot',size=26)
f.edge('dot1','dot-user','dot-entry',[(1040,370),(1040,450)],kind='teal')
f.edge('dot2','dot-entry','dot-target',[(1040,595),(1040,660)],kind='teal')
f.text('dot-note',775,810,530,70,['浏览器出站代理另有配置记录','不能把它画成已确认的 GUI 传输链'],22)
f.node('unknown',100,960,1200,120,'两边仍须分别验收',['公网入站、长期服务与恢复；Dot 另缺独立 SSH 及尾网连接证据'],kind='amber',size=25)
f.text('source',60,1120,1280,40,['来源：[W1 第 7 章][W2 第 6 节][W3][A #027、#036、#060][U1][O1]。'],22)
finish(f,'图中区分 WorkBuddy 已建立的尾网管理入口与 Dot 的人工接管入口。两条路径没有可比的 GUI 延迟数据，公网出口或通配监听也不证明入站可达。','[W1][W2][W3][A][U1][O1]')

f=Figure('04-persistence-comparison','图 4  数据保留与恢复的比较','蓝色：历史存储或服务证据；青色：官方能力；橙色：待验证对象',1400,1110)
f.node('dot',70,190,600,150,'Dot 状态延续〔官方〕',['可跨使用时段保留状态','本账号的具体策略尚未核实'],kind='teal',size=27)
f.node('wb',730,190,600,150,'WorkBuddy 存储与同步〔实测〕',['user-data 与后端挂载线索','同步组件运行，完整性尚未验收'],size=27)
f.group('objects',70,450,1260,320,'两边都需要按对象与生命周期事件核验')
for key,x,title,body in [('files',100,'文件与目录',['路径和哈希','暂停或重建后是否恢复']),('browser',525,'浏览器会话',['是否已登录','网站过期与快照分别看']),('process',950,'进程与连接',['进程、端口与 TCP','是否继续或需要重建'])]:
    f.node(key,x,545,350,175,title,body,parent='objects',kind='amber',size=24)
f.edge('dot-test','dot','objects',[(370,340),(370,450)],kind='amber')
f.edge('wb-test','wb','objects',[(1030,340),(1030,450)],kind='amber')
f.node('backup',160,870,1080,135,'独立副本与恢复演练〔建议〕',['状态保留不等于进程持续运行；文件同步不等于可恢复备份','当前没有一方完成本项目所需的完整恢复验收'],kind='amber',size=26)
f.text('source',60,1045,1280,40,['来源：[W1 第 3、5、11 章][A #039、#042][O1][O2]；虚线不表示已建立备份。'],22)
finish(f,'两边各有不同证据：一边是产品状态说明，一边是实例存储与同步观察。完整目录规则、恢复结果和持续运行保障仍需分别验证，不能直接评定谁更可靠。','[W1][A][O1][O2]')

f=Figure('05-gui-workflow','图 5  人工操作与控制权交接','青色：Dot 官方流程；蓝色：WorkBuddy 历史实测；橙色：未确认',1400,1180)
f.group('left',50,170,620,785,'Dot 人工介入流程')
f.group('right',730,170,620,785,'WorkBuddy 已验证界面范围')
steps=[('open',260,'打开云电脑',['查看画面']),('take',425,'Take over',['取得鼠标与键盘控制']),('act',590,'完成必要操作',['例如登录或检查结果']),('return',755,'Return control',['交还后由 Dot 继续任务'])]
for key,y,title,body in steps:
    f.node(key,90,y,540,110,title,body,parent='left',kind='teal',size=26)
for (a,y,*_),(b,ny,*_) in zip(steps,steps[1:]):
    f.edge(a+b,a,b,[(360,y+110),(360,ny)],kind='teal')
f.node('terminal',770,260,540,155,'终端与预览组件〔实测〕',['平台终端、editor-sdk 运行','VS Code 配置按需启动'],parent='right',size=26)
f.node('desktop',770,500,540,170,'完整桌面〔未验收〕',['有相关软件包不等于运行会话','不能直接视为 Dot 的 GUI 替代品'],parent='right',kind='amber',size=25)
f.node('same-test',770,755,540,110,'同场景 GUI 对照〔缺失〕',['没有足够证据评定哪边更好用'],parent='right',kind='amber',size=24)
f.text('meaning',75,995,1250,90,['〔推断〕交接流程支持“围绕代理任务组织交互”的解释。','它不能证明界面简陋是刻意设计，或安全、成本与代理工作的必要代价。'],25)
f.text('source',60,1120,1280,40,['来源：[O1][O3][W1 第 4、5 章][U1]；不是 GUI 性能测试。'],22)
finish(f,'Dot 有明确的人机交接流程，WorkBuddy 现有证据主要覆盖终端与预览组件。入口存在、操作友好和传输流畅应分开验收；图示不推测内部产品决策。','[O1][O3][W1][U1]')

f=Figure('06-gui-diagnosis','图 6  GUI 体验问题的定位逻辑','通用诊断框架〔建议〕｜所有候选原因待核验，不是 Dot 已测架构',1400,1180)
f.node('complaint',360,180,680,110,'用户反馈〔观察〕',['界面简陋、总体使用体验差'],size=27)
f.node('layout',70,420,600,160,'找不到或不理解操作',['检查入口、状态反馈与步骤','记录任务用时、误操作和恢复路径'],kind='amber',size=26)
f.node('response',730,420,600,160,'动作发出后等待或异常',['先核对接管与输入焦点','再区分全界面问题和单应用问题'],kind='amber',size=26)
f.edge('branch1','complaint','layout',[(530,290),(530,355),(370,355),(370,420)],kind='amber')
f.edge('branch2','complaint','response',[(870,290),(870,355),(1030,355),(1030,420)],kind='amber')
f.group('chain',70,690,1260,220,'按键到可见结果的概念链〔通用技术分析〕')
nodes=[('input',100,'输入与控制权'),('app',410,'应用与资源'),('frame',720,'画面与传输'),('client',1030,'客户端呈现')]
for key,x,title in nodes:
    f.node(key,x,775,270,85,title,[],parent='chain',kind='slate',size=24)
for (a,x,_),(b,xx,_) in zip(nodes,nodes[1:]):
    f.edge(a+b,a,b,[(x+270,817),(xx,817)],kind='slate')
f.text('notes',75,965,1250,100,['分别记录步骤、输入回显、应用耗时与画面表现；有条件时再采集资源及链路指标。','Dot 协议、编码与帧率仍未知；WorkBuddy 的尾网 RTT 不能填入这条 GUI 链。'],25)
f.text('source',60,1110,1280,45,['来源：[U1][T3][H1][W3]；借用诊断方法，不认定 Dot 使用 RDP 或 Azure Virtual Desktop。'],22)
finish(f,'首先区分信息与操作设计问题，以及响应与执行问题。概念链只用于提出应采集的证据；各阶段可能并行或采用不同实现，不是可直接相加的实测延迟公式。','[U1][T3][H1][W3]')

for f in FIGURES:
    p=OUT/(f.key+'.svg');p.write_text(svg(f))
    drawio([f],OUT/(f.key+'.drawio'))
    subprocess.run(['/usr/bin/rsvg-convert','--width',str(f.w*2),'--height',str(f.h*2),'-o',str(OUT/(f.key+'.png')),str(p)],check=True)
    with Image.open(OUT/(f.key+'.png')) as im:
        im.thumbnail((1400,1400));im.convert('RGB').save(BASE/'sources'/(f.key+'-preview.jpg'),quality=94)
drawio(FIGURES,OUT/'CodexDot与WorkBuddy完整图集.drawio')
(BASE/'sources/diagram-manifest.json').write_text(json.dumps(META,ensure_ascii=False,indent=2))
print('Built six diagrams in PNG, SVG and editable draw.io, plus the full six-page draw.io.')
