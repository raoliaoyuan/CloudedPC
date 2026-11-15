from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from pathlib import Path

OUT = Path('/home/gamer/Work/CloudPC/audit-2026-11-10')
d = Document()
s = d.sections[0]
s.page_width, s.page_height = Cm(21), Cm(29.7)
s.top_margin, s.bottom_margin = Cm(1.8), Cm(1.8)
s.left_margin, s.right_margin = Cm(2), Cm(2)
s.footer_distance = Cm(.8)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3']:
    st=d.styles[name]
    st.font.name='Noto Sans CJK SC'
    st.element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Noto Sans CJK SC')
    st.font.color.rgb=RGBColor(0,0,0)
    st.paragraph_format.space_after=Pt(6)
    st.paragraph_format.line_spacing=Pt(15)
    for el in st.element.xpath('.//w:pBdr'):
        el.getparent().remove(el)
    snap=OxmlElement('w:snapToGrid');snap.set(qn('w:val'),'0');st.element.get_or_add_pPr().append(snap)
for grid in s._sectPr.findall(qn('w:docGrid')):s._sectPr.remove(grid)
d.styles['Normal'].font.size=Pt(10)
d.styles['Title'].font.size=Pt(24)
d.styles['Heading 1'].font.size=Pt(17)
d.styles['Heading 2'].font.size=Pt(12)
d.styles['Heading 1'].paragraph_format.space_before=Pt(4)
d.styles['Heading 2'].paragraph_format.space_before=Pt(9)
for name,points in [('Title',32),('Subtitle',19),('Heading 1',24),('Heading 2',18)]:
    d.styles[name].paragraph_format.line_spacing=Pt(points)
d.core_properties.title='云 PC 软硬件配置与运行检查报告'
d.core_properties.subject='workbuddy-sandbox 只读检查'
d.core_properties.author='Codex'
f=s.footer.paragraphs[0]; f.alignment=WD_ALIGN_PARAGRAPH.RIGHT
f.add_run('2026 年 11 月 10 日  ·  ')
fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),'PAGE'); f._p.append(fld)
for r in f.runs:r.font.size=Pt(8)

def p(t,style=None):return d.add_paragraph(t,style)
def h(t):d.add_heading(t,2)
def page(t):d.add_heading(t,1).paragraph_format.page_break_before=True
def table(headers,rows,widths):
    t=d.add_table(rows=1, cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    for c,w in zip(t.columns,widths):c.width=Cm(w)
    for c,txt in zip(t.rows[0].cells,headers):c.text=txt
    for row in rows:
        for c,txt in zip(t.add_row().cells,row):c.text=str(txt)
    for ri,row in enumerate(t.rows):
        pr=row._tr.get_or_add_trPr()
        cant=OxmlElement('w:cantSplit');pr.append(cant)
        if ri==0:pr.append(OxmlElement('w:tblHeader'))
        for ci,c in enumerate(row.cells):
            c.width=Cm(widths[ci]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcpr=c._tc.get_or_add_tcPr()
            borders=OxmlElement('w:tcBorders')
            for side in ['top','left','bottom','right']:
                b=OxmlElement('w:'+side);b.set(qn('w:val'),'single');b.set(qn('w:sz'),'4');b.set(qn('w:color'),'D9D9D9');borders.append(b)
            tcpr.append(borders)
            shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E8EEF4' if ri==0 else ('F7F8FA' if ri%2==0 else 'FFFFFF'));tcpr.append(shade)
            mar=OxmlElement('w:tcMar')
            for edge in ['top','bottom','left','right']:
                e=OxmlElement('w:'+edge);e.set(qn('w:w'),'85');e.set(qn('w:type'),'dxa');mar.append(e)
            tcpr.append(mar)
            for par in c.paragraphs:
                par.paragraph_format.space_after=Pt(1);par.paragraph_format.line_spacing=Pt(13)
                for r in par.runs:r.font.size=Pt(9);r.bold=ri==0
    blank=p('');blank.paragraph_format.space_after=Pt(0);blank.paragraph_format.line_spacing=Pt(3)

def source(label,url):
    par=d.add_paragraph()
    link=OxmlElement('w:hyperlink');link.set(qn('r:id'),par.part.relate_to(url,RT.HYPERLINK,is_external=True))
    r=OxmlElement('w:r');pr=OxmlElement('w:rPr');color=OxmlElement('w:color');color.set(qn('w:val'),'245A81');pr.append(color);r.append(pr)
    text=OxmlElement('w:t');text.text=label;r.append(text);link.append(r);par._p.append(link)
    par.paragraph_format.space_after=Pt(4)

d.add_heading('云 PC 软硬件配置与运行检查报告',0)
p('检查对象  workbuddy-sandbox  ·  100.120.78.38','Subtitle')
p('检查时间：2026 年 11 月 10 日 15:56–16:01，新加坡时间 UTC+8。')
p('这是一套运行在腾讯云 CVM 虚拟机上的 Linux 容器开发环境。当前可见资源限制为 4 核 CPU 算力、8 GiB 内存，根文件系统显示 256 GiB 容量。检查时资源余量充足，SSH 连接可用；需要优先处理的是登录环境错误、软件更新积压、独立 OpenSSH 的宽松认证配置，以及远程连接的自动恢复保障。')
table(['项目','实测结果','判断'],[
('运行形态','Ubuntu 24.04.3 LTS，Docker 容器','适合作为开发工作区'),
('CPU 配额','400000 / 100000 = 4 核等效上限','不是独占 32 核'),
('内存限制','8 GiB；采样约用 1.48 GiB','约用 18.5%'),
('根目录容量','256 GiB；可用约 253.79 GiB','持久化承诺待平台确认'),
('GPU 与 KVM','未见 GPU、/dev/dri、/dev/kvm','无可验证硬件加速'),
('Tailscale','在线，用户态模式，SSH 已启用','5 次探测均走 DERP'),
('连接延迟','103–106 ms，均值 104.6 ms','短样本稳定，非带宽测试'),
('系统更新','281 个候选更新，其中 221 个在安全源','需要维护窗口处理'),
('启动脚本','已定位 Node、pyenv、rustup 三类问题','可修复的软件配置问题')
],[3,8.2,5.8])
h('检查结论')
p('当前更适合远程编程、脚本执行、小型服务、轻量 Docker 开发和文档处理。不能按 32 核、123 GiB 内存的机器安排任务，也不具备已验证的 GPU 计算、游戏串流或完整桌面能力。生产服务的连续运行能力，还取决于平台休眠、回收、数据保留和网络策略。')
p('本次仅执行读取、短时资源采样、网络诊断和隔离模块导入验证。没有升级软件、修改配置、重启服务、运行磁盘写入压测或全负载压力测试。SSH 登录与诊断会产生正常连接日志和少量流量。')

page('1 运行环境与实际计算资源')
h('环境身份与边界')
p('Tailscale 名称为 workbuddy-sandbox，容器 hostname 为 064f56bb22e3。系统用户态是 Ubuntu 24.04.3 LTS，内核为 6.6.117-45.14.1.tl4.x86_64；DMI 显示 Tencent Cloud / CVM，CPU 虚拟化层显示 KVM，systemd-detect-virt 返回 docker。PID 1 为 docker-init，平台主要由 supervisord 管理服务。')
p('这些证据表明存在“腾讯云虚拟机 → 容器开发工作区”的层级。Ubuntu 用户态版本不代表运行的是 Ubuntu 标准内核。内核、微码、物理硬件及更上层资源限制主要由平台控制。')
table(['资源','系统可见值','本工作区的解释'],[
('处理器型号','AMD EPYC 9754 128-Core Processor','型号字符串不代表分配了 128 核'),
('CPU 拓扑','32 逻辑 CPU；16 核 × 2 线程','上层虚拟 CPU 拓扑'),
('CPU 带宽','cpu.max = 400000 100000','每 100 ms 合计最多 400 ms CPU 时间'),
('CPU 亲和性','0–31，nproc = 32','可调度范围大于实际配额'),
('内存可见总量','132411875328 B，约 123.32 GiB','free 显示上层内存视图'),
('内存硬限制','memory.max = 8589934592 B','本容器上限为 8 GiB'),
('交换空间','free 显示 0；swap.current = 0','未发现可用交换空间'),
('指令集','AVX2、AVX-512、AES 等可见','未单独执行指令兼容基准')
],[3.1,6.3,7.6])
h('资源限制如何生效')
p('进程所在 init.scope 的 cpu.max 和 memory.max 都显示 max，但其可见父 cgroup 设置了 4 核和 8 GiB 的限制，子级仍受父级约束。因此，只读叶子节点或 Docker info 都可能高估资源。此处 4 核是 CPU 时间配额，不是 4 个独占物理核，也不是平台性能保证。[1]')
p('memory.swap.max 虽然为 8 GiB，但它只是允许使用交换空间的上限，不能解释成额外赠送了 8 GiB 可用 RAM。实际采样没有交换空间使用。')
h('GPU 与虚拟化设备')
p('未发现 /dev/nvidia*、/dev/dri、/dev/kvm，且 nvidia-smi 不可用。已安装 NVIDIA 容器组件或存在 CUDA 安装日志，均不能证明分配了 GPU。当前无法验证 CUDA 计算、硬件编解码或 KVM 嵌套虚拟化能力。')

page('2 资源健康与存储')
table(['指标','检查结果','含义'],[
('内存当前用量','约 1.48 GiB / 8 GiB','距硬限制约 6.52 GiB，不等于应用可全部占用'),
('内存历史峰值','约 1.55 GiB','仅覆盖当前 cgroup 生命周期'),
('内存事件','max、oom、oom_kill 均为 0','未记录触顶或 OOM 杀进程'),
('CPU 短时采样','5 秒内约用 0.03185 核','约为 4 核配额的 0.80%'),
('CPU 节流','累计 5 次；样本内新增 0 次','累计节流时间约 1.06 秒'),
('资源压力 PSI','CPU、内存、I/O 的 avg10/60/300 为 0','采样时未见明显压力'),
('网络接口计数','eth0 收发错误及丢弃均为 0','仅为当前计数器范围'),
('包状态','dpkg --audit 无输出','未发现 dpkg 未完成配置问题')
],[3.2,6.3,7.5])
p('主机可见 load average 约为 3.95 / 4.10 / 3.75，vmstat 也包含上层视图。它们不能直接说明本容器已经吃满 4 核。本报告优先使用 cgroup 增量和硬限制判断资源状态。没有对 CPU 做持续压测，不能据此保证高负载时的性能或长期稳定性。')
h('容量与文件系统')
p('根目录 / 是 overlay 文件系统，总量 274877906944 B，即 256 GiB；可用 272497704960 B，约 253.79 GiB；已用约 233.6 MiB，df 四舍五入显示 1%。/root、/workspace、/tmp 均落在该根文件系统。')
p('可写层位于平台 user-data 路径，另可见 btrfs /dev/nbd962 的 256 GiB 后端。这是持久化存储结构的线索，但不足以证明停机、休眠、重建、到期回收后的保留规则。overlay 的已用量也不代表预装镜像和全部软件的实际体积。')
p('lsblk 另显示 vda 约 1000 GiB、vdb 2 TiB、vdc 100 GiB，以及 /.oldroot 等平台挂载。它们不能简单相加为你可独占使用的磁盘。虚拟磁盘的 ROTA=1 也不足以确认物理介质为机械硬盘。')
h('存储健康的核验范围')
p('可见文件系统没有容量紧张迹象；overlay/btrfs 的 inode 数显示为 0 或不适用，不能按普通 ext4 的固定 inode 表解读。本次未执行 SMART、fsck、fio、dd 或写入压力测试，因此无法判断底层磁盘寿命、真实 IOPS、吞吐量、写入延迟和物理坏块。')
p('/dev/shm 显示 8 GiB tmpfs，但不是额外独立内存。大规模共享内存、浏览器并发、编译和 Docker 容器仍需共同遵守 8 GiB 的资源边界。')

page('3 网络与 Tailscale 连接')
table(['项目','检查结果'],[
('目标 Tailscale 地址','100.120.78.38；workbuddy-sandbox'),
('本次连接端','steam-os，100.82.31.127'),
('云端内网','eth0 为 172.24.0.11/24；默认网关 172.24.0.1'),
('Docker 网桥','172.17.0.1/16；无运行容器，网桥 DOWN'),
('DNS','183.60.83.19、183.60.82.98'),
('Tailscale 版本及状态','1.104.5；Running；Health 列表为空'),
('工作模式','TUN=false；--tun=userspace-networking'),
('本机代理','云端 SOCKS5 监听 localhost:1055'),
('远程访问','RunSSH=true；已实际通过 Tailscale SSH 登录'),
('节点密钥到期','2027 年 5 月 9 日 15:42:07，新加坡时间'),
('Serve 与 Funnel','均没有配置'),
('路由设置','接收路由已开启；没有通告子网；没有选择出口节点')
],[4.5,12.5])
h('路径与延迟')
p('从 steam-os 发出的 5 次 Tailscale ping 分别为 106、105、103、104、105 ms，均经 DERP(sin) 中继，短样本中 5 次均成功。平均 104.6 ms、跨度 3 ms；这不是长期丢包率、业务响应时间或吞吐量测试。')
p('云端 netcheck 显示 UDP=true，MappingVariesByDestIP=true，公网 IPv6 不可用；到新加坡 DERP 约 1.8 ms。本地 netcheck 显示 UDP=false，未探测到公网 IPv4 地址，使用本地 HTTP 代理 127.0.0.1:18080，到新加坡 DERP 约 101.5 ms。')
p('综合判断，本地 UDP 探测不通和云端随目的地址变化的 NAT 映射，是当前难以直连的主要线索。测量也提示延迟主要在本地到中继的路径；它不能证明代理是唯一原因，也不能精确定位哪一层防火墙阻断了 UDP。[3]')
h('对使用的影响')
p('约 105 ms 的往返延迟通常能支持 SSH 和代码编辑，但高频交互、大文件同步或远程图形体验需要额外实测。先核查本地代理、VPN、路由器和出口网络的 UDP 能力，再考虑云端 NAT 与平台限制；不宜仅靠更换 DNS 期待变为直连。')
p('用户态模式不创建普通 tailscale0 网卡；应用出站访问尾网可能需要 SOCKS5/HTTP 代理。当前 SSH 可用，并不等于普通 ping、所有应用或整个本地 LAN 都已经透明互通。是否覆盖局域网子网还需核实子网路由及控制台策略。[2]')

page('4 软件栈与服务运行状态')
table(['组件','已验证版本或状态','说明'],[
('系统 Python','3.12.3；pip 24.0','默认非交互式 SSH 环境可用'),
('pyenv Python','3.11.1；pyenv 2.3.9 开发标识','文件存在，但默认 PATH 找不到 pyenv'),
('系统 Node.js','18.19.1，/usr/bin/node','默认非交互式 SSH 优先选中'),
('NVM Node.js','22.13.1','NVM 默认别名也指向该版本'),
('NVM 下的 npm','11.9.0','默认 SSH PATH 中 npm 不可用'),
('前端工具','pnpm 10.28.2、TypeScript 5.9.3','版本来自全局 package.json'),
('前端 CLI','Angular CLI 21.1.3、Vue CLI 5.0.9','依赖与系统 Node 18 混用存在问题'),
('浏览器工具','Playwright 1.58.1','未执行浏览器端到端测试'),
('Git 与 SSH','Git 2.43.0；OpenSSH 9.6p1','OpenSSH 包修订为 Ubuntu 3ubuntu13.20'),
('Docker','Engine 27.5.1；containerd 1.7.25','daemon 可查询，无容器、无镜像'),
('容器运行时','runc 1.2.4；overlay2；cgroup v2','嵌套 Docker 开发环境'),
('编译工具','gcc、g++、cmake、make 存在','未执行编译和工具链兼容测试')
],[3,6.3,7.7])
p('系统 Python 包包含 NumPy 1.26.4、Pillow 10.2.0、requests 2.31.0 等。平台还预装 PM2、CodeBuddy、文档及浏览器相关工具。本次列出系统包和已发现的全局工具，不等于审计了所有项目虚拟环境或项目依赖。')
h('服务管理')
p('正在运行的核心进程包括 supervisord、平台 node 服务、sandbox-proxy、envd、sync_server、editor_sdk、dockerd、containerd、tailscaled、sshd 和 PM2。systemctl 不能作为该环境的有效健康检查入口，因为 PID 1 不是 systemd；其离线或连接失败输出不应直接判为系统故障。')
p('Docker info 自身显示 32 CPU 和约 123 GiB 内存，但仍应按外层 cgroup 的 4 核 / 8 GiB 来控制容器总资源。在嵌套容器内再设合理限制，避免多个任务同时把外层工作区挤到 OOM。')
h('图形桌面能力')
p('软件包中存在桌面、noVNC、Xvfb 等组件，但进程检查没有发现 Xorg、Xvfb、VNC、RDP、GNOME 或 XFCE 会话。因此本次只能确认命令行与平台开发服务在运行，不能确认完整远程桌面已配置完成。')

page('5 登录报错的原因与处理建议')
h('Node.js 与 yargs 的模块错误')
p('触发入口是 /root/.bashrc.d/50-node 第 2 行的 ng completion script。它在每次交互式 shell 初始化时运行 Angular CLI 的补全生成。第 1 行加载的 nvm-lazy.sh 把 Node 22 的 bin 目录追加到 PATH 尾部，系统 /usr/bin/node 仍排在前面。')
p('检查发现系统 Node 是 18.19.1，而 NVM 中 Angular CLI 21.1.3 的 yargs 18.0.0 要求 Node ^20.19.0、^22.12.0 或 >=23。用两个 Node 可执行文件分别 require 同一 helpers.mjs：Node 18 返回 ERR_REQUIRE_ESM，Node 22.13.1 成功。该隔离验证复现了截图中的错误，明确支持“运行时选择不一致”这一原因。[5]')
p('建议：先统一交互终端、SSH 非交互命令及服务进程的 Node 版本与 PATH，再按实际需要启用 Angular 补全。优先修正环境入口，不直接修改第三方 node_modules 文件；随后在新会话里验证 node、npm、ng 的实际路径及版本。')
h('pyenv command not found')
p('触发入口是 /root/.bashrc.d/60-python 第 108 行的 eval "$(pyenv init -)"。/root/.pyenv/bin/pyenv 确实存在，使用绝对路径能返回版本；其 Python 3.11.1 也能运行。但是默认 SSH PATH 不包含该 bin 目录。')
p('建议：在调用 pyenv init 前正确设置 PYENV_ROOT 与 PATH，并加上 command -v 检查。脚本中还有依赖 CloudStudio 环境变量的目录、软链接和编辑器设置逻辑，应区分平台终端与普通 SSH 会话，避免把平台初始化无条件带入所有 shell。')
h('mv cannot stat 空路径')
p('触发入口是 /root/.bashrc.d/80-rust 第 4 行：当 /workspace/.cargo/bin/rustup 不存在时，尝试移动 command -v rustup 的结果。默认 PATH 找不到 rustup，命令替换为空，于是出现截图中的 mv 空路径错误。实际 /root/.cargo/bin/rustup 文件存在。')
p('建议：先检查源可执行文件是否存在及目标目录是否需要迁移，并让初始化可重复执行。更稳妥的方案是修正 CARGO_HOME/PATH 或遵从平台的工具链持久化约定，避免每次登录都移动工具。')
h('修复后的验收条件')
p('重新打开 SSH 交互会话应无上述三条报错；非交互执行 node --version、npm --version、python3 --version 应符合预期；pyenv 和 rustup 在需要的会话内可定位。还需验证平台编辑器和后台服务没有因 PATH 调整使用到错误运行时。本次没有改动这些文件，也没有执行包含移动和写入操作的完整启动脚本。')

page('6 访问控制与安全配置')
h('两套 SSH 入口需要分别管理')
p('Tailscale RunSSH=true，当前会话的父进程链属于 tailscaled 的 SSH 子进程，证明本次访问由 Tailscale SSH 处理。其授权依赖尾网访问规则及 SSH 策略；本次没有读取管理控制台策略，不能断言当前授权范围足够收敛。[4]')
p('此外，系统 OpenSSH 正在 0.0.0.0:22 和 [::]:22 监听。sshd -t 检查通过，sshd -T 及针对 root 的配置评估显示 PermitRootLogin=yes、PasswordAuthentication=yes、PubkeyAuthentication=yes；root 密码状态为 P。说明存在可尝试 root 密码认证的独立入口，但本次没有测试密码强度，也未验证其公网可达性。[7]')
table(['检查项','发现','优先建议'],[
('OpenSSH 认证','允许 root 密码认证；空密码禁止','验证替代管理入口后收紧认证'),
('监听范围','SSH 及多个平台端口绑定通配地址','核对平台端口发布与来源限制'),
('本地防火墙','iptables/nft 默认 INPUT 为 ACCEPT','不能替代云端安全组审计'),
('Tailscale 密钥文件','目录 700、state 文件 600','当前权限较合理'),
('进程权限','多数服务以 root 运行','自建服务尽量使用普通用户'),
('容器能力','可见 CapEff 较宽；Seccomp=2','保留 seccomp，避免进一步放宽权限'),
('失败登录','btmp 两条 root 失败，来源 127.0.0.1','不能据此判定入侵'),
('系统日志','journald 无日志文件','需确认平台日志和认证日志留存')
],[3,6.5,7.5])
h('已发现的监听端口')
p('全接口监听包括 TCP 22、65310、65213、65216、65225、49983、9090、18601，关联 SSH、平台 node、sandbox-proxy、envd、sync_server。localhost 上另有 1055、8089、39099、62667；Tailscale 还使用 UDP 端口及回环绑定的 PeerAPI。端口号可能随进程重启变化。')
p('通配地址监听不等于公网开放。容器 NAT、平台代理、云安全组和尾网策略都可能影响可达性；反过来，平台端口转发也可能发布容器内部服务。本次没有外网扫描，也没有验证上述平台 API 的认证逻辑。')
h('内核与 CPU 安全标志')
p('lscpu 对 Spec rstack overflow、Spec store bypass、Tsa 显示 Vulnerable 或缺少微码；部分 Spectre 项显示已有缓解。这属于上层内核向容器呈现的状态，需要平台确认宿主内核和微码修复。不能仅凭这些字符串认定漏洞可实际利用，也不宜在工作区内自行升级共享内核。')

page('7 更新维护与持续运行')
h('软件更新积压')
p('APT 缓存识别到 871 个已安装包、281 个可升级包，其中 221 个候选版本出现在 noble-security 源。主要 Ubuntu 更新与安全索引的时间为 2026 年 11 月 9 日。本次没有刷新索引，因此这是现有缓存的检查结果；221 是包数量，不是 221 个独立漏洞。')
p('待更新项涉及 OpenSSL、Python、curl、sudo、glibc、图形与解析库等。系统 /usr/bin/node 的 Node 18 分支已结束上游支持；Ubuntu 包的安全维护仍需结合发行版修订版本判断，不能只看上游版本号判定所有漏洞未修复。[6]')
p('建议由平台支持的镜像升级流程或经过备份的维护窗口处理，先确认自动化工具、编辑器和平台 agent 的兼容性。NVIDIA 容器组件的现有版本含 rc 标识，也有稳定版候选；无 GPU 分配时不必为了“补齐硬件”盲目安装驱动。未发现 reboot-required 标记，但这不能证明共享内核已经完成所有必要更新。')
h('远程连接的恢复保障')
p('tailscaled 于 15:40:51 启动，sshd 于 15:45:19 启动，均直接挂在 PID 1 下。已读取的平台 Supervisor 主配置、相关片段及补充目录中没有发现 Tailscale 或 sshd 的守护条目。未能确认它们的自动启动机制，也没有执行停止、重启或实例重建测试。')
p('建议把需要长期运行的服务纳入平台支持的启动与守护机制，并验证“进程退出后恢复、工作区重启后恢复、平台休眠后恢复”三个不同场景。由于环境不是 systemd，直接使用 systemctl enable 不足以完成这项工作。')
h('数据与日志')
p('当前未从所查工具和 cron 入口中确认备份任务；这不排除平台有快照或外部备份。应明确 /workspace、/root、Docker 数据、Tailscale 状态文件各自的保留规则，并做一次小文件恢复演练。仅保存软件安装命令或仅把代码推入 Git，不能覆盖数据库和运行状态的恢复。')
p('journald 无记录，部分日志由平台 log-forward-tee、sandbox-log-collector 等组件转发；本次没有读取平台日志后台。应确认认证失败、进程异常、OOM、磁盘容量和关键服务退出能够被记录并保留。')
h('使用建议')
p('按 4 核 / 8 GiB 配置规划任务：普通开发、自动化、小型 Web/API、轻量容器比较匹配；大型并行编译、多浏览器会话和数据分析需要监测内存。GPU 训练、硬件视频编码、KVM 虚拟机和高性能图形桌面不属于当前已验证能力。没有跑应用基准，不能给出确定吞吐量或并发容量。')

page('8 整改顺序与验收清单')
table(['优先级','行动','完成判据'],[
('P1 尽快','收紧独立 OpenSSH 与尾网 SSH 授权','保留可用管理通道；仅授权用户和来源可登录'),
('P1 尽快','确认数据持久化并建立可恢复备份','完成一次恢复演练；记录回收与保留规则'),
('P1 尽快','处理安全源更新与平台镜像维护','备份后升级；核心工具与服务回归通过'),
('P1 尽快','统一 Node、pyenv、Rust 的启动环境','新交互终端无错误；非交互命令路径一致'),
('P2 随后','配置 Tailscale 等服务的自动恢复','进程异常、工作区重启后均能恢复访问'),
('P2 随后','排查本地 UDP 与云端 NAT','重新 ping/netcheck；记录直连或中继结果'),
('P2 随后','补齐日志、容量和内存监控','可查认证与退出日志；有资源告警机制'),
('P3 按需','测试业务性能及图形桌面','以实际任务测量耗时、并发、内存与延迟')
],[2.4,6.3,8.3])
p('P1 表示建议优先处理，并不代表已经发生入侵或故障。任何 SSH、防火墙、网络或启动配置调整，都应保留现有连接和平台控制台入口，并在新会话验证成功后再关闭旧入口。报告中的整改项尚未实施。')
h('建议复检指标')
p('资源：定期读取父 cgroup 的 cpu.max、memory.max、memory.current、memory.events 和 cpu.stat 增量；不要仅用 free、nproc、Docker info。服务：核对 Supervisor 状态、进程退出码、端口和平台日志。网络：记录 Tailscale 版本、Health、RunSSH、密钥到期时间，以及实际 peer 路径。')
h('仍需平台或用户侧补充核验')
p('云产品具体套餐与计费规格、底层磁盘类型/IOPS、物理机健康、宿主内核与微码修复、平台自动休眠和生命周期、用户数据保留承诺、快照与恢复点、云安全组及平台端口发布、尾网 ACL/SSH policy，都无法仅从当前容器会话完整确认。')
p('也未执行长时间性能和稳定性压测、磁盘写入基准、互联网带宽测试、应用端到端测试、密码强度验证、完整漏洞扫描或恶意软件取证。因此，“检查时未见资源压力”不等于硬件全面无故障，“当前可登录”也不等于重启后可自动恢复。')

page('9 检查证据与参考资料')
h('本次检查证据')
p('目标通过截图中的地址及 Tailscale 在线节点对应关系确认；SSH 采用既有主机校验和非交互认证。主要采集时间为 15:57–16:01，新加坡时间。报告使用的是该时间段的快照，不代表之后的配置变化。')
table(['本地证据文件','主要内容'],[
('evidence.txt','系统、CPU、内存、磁盘、网络、端口、软件包与更新清单'),
('followup.txt','cgroup 父子限制、5 秒采样、Tailscale、Docker 与软件统计'),
('startup.txt','shell 启动片段、工具版本、进程时间与日志元数据'),
('final-check.txt','PATH、NVM 懒加载、隔离 ESM 导入与失败登录记录'),
('service-check.txt','实际平台 Supervisor 配置中的服务与自动启动条目'),
('local-netcheck.txt','连接端 UDP 探测、中继延迟与代理线索'),
('collect.sh 等脚本','可复核的读取命令；后续运行应重新检查适用环境')
],[5.2,11.8])
p('证据位于本报告同目录 audit-2026-11-10。原始文件含内部地址、服务路径等环境信息，适合在自己的管理范围内留存。未读取私钥、密码散列或 Tailscale 状态文件内容。')
h('官方解释资料')
p('以下资料用于解释配置语义与建议；机器规格、运行状态和版本以本次实测为依据。访问日期为 2026 年 11 月 10 日。')
source('[1] Linux Kernel 文档  cgroup v2 的 CPU 与内存资源限制','https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html')
source('[2] Tailscale 文档  容器用户态网络模式','https://tailscale.com/docs/concepts/userspace-networking')
source('[3] Tailscale 文档  设备连通性与 NAT 诊断','https://tailscale.com/docs/reference/device-connectivity')
source('[4] Tailscale 文档  Tailscale SSH 与访问授权','https://tailscale.com/docs/features/tailscale-ssh')
source('[5] Node.js 22.12 发布说明  require 对 ESM 的支持','https://nodejs.org/en/blog/release/v22.12.0')
source('[6] Node.js 官方版本与支持状态','https://nodejs.org/en/about/previous-releases')
source('[7] OpenSSH 官方 sshd_config 配置说明','https://man.openbsd.org/sshd_config')
p('单位说明：GiB 为 2³⁰ 字节，MiB 为 2²⁰ 字节；CPU 核数配额由 quota / period 计算。容量、内存和延迟均保留了必要的测量范围与解释边界。')

d.save(OUT/'云PC软硬件检查报告.docx')
print(OUT/'云PC软硬件检查报告.docx')
