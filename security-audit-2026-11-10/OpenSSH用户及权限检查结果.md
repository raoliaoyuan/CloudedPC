# OpenSSH 用户及权限检查结果

检查时间：2026 年 11 月 10 日 16:57，新加坡时间（UTC+8）。

检查对象：WorkBuddy Linux 执行容器 `064f56bb22e3`，Tailscale 节点 `workbuddy-sandbox`，地址 `100.120.78.38`。

本次采用只读检查，核对本地账号、组成员关系、密码状态标记、有效 SSH 配置、授权公钥文件是否存在，以及 sudo 授权。没有尝试密码登录，没有读取密码散列或私钥，没有修改配置。

## 结论

**OpenSSH 没有独立的用户库，它使用容器内的 Linux 系统账号。** 当前有 27 个本地账号，其中与日常使用最相关的是 `root`、`ubuntu`、`user`。

`root` 是容器内管理员；`ubuntu` 和 `user` 虽然使用非零 UID，但均具有免密码执行任意 root 命令的 sudo 权限，因此不能作为运行不可信程序的低权限账号。

## 用户与权限清单

| 用户 | UID | Shell | 当前认证状态 | 登录后的权限 |
| --- | ---: | --- | --- | --- |
| **root** | 0 | `/bin/bash` | 已设置密码；OpenSSH 允许 root 密码登录；未配置授权公钥 | **容器内管理员**，可管理文件、账号、软件和服务 |
| **ubuntu** | 1000 | `/bin/bash` | 密码锁定；未配置授权公钥 | 初始为普通用户，但可**免密码 sudo 执行任意 root 命令** |
| **user** | 1001 | `/bin/sh` | 密码锁定；未配置授权公钥 | 初始为普通用户，但可**免密码 sudo 执行任意 root 命令** |
| `dockremap` | 996 | `/bin/sh` | 密码锁定；未配置授权公钥 | 系统账号，无 sudo 权限 |
| `nova` | 101 | `/bin/bash` | 密码锁定；未配置授权公钥 | 系统账号，无 sudo 权限 |
| `sync` | 4 | `/bin/sync` | 密码锁定；未配置授权公钥 | 特殊系统账号，无 sudo 权限；Shell 不是交互式命令行 |

“未配置授权公钥”是指上述账号主目录下的 `.ssh/authorized_keys`、`.ssh/authorized_keys2` 均不存在。有效 SSH 配置也未设置额外的公钥查询命令或受信任用户证书 CA。

密码状态检查中，`root` 为 `P`，其余上述账号为 `L`。这些状态只说明密码是否设置或锁定，不代表已经实测登录成功，也不代表密码强度已经得到验证。

## 组成员与 sudo 权限

当前相关组成员关系如下：

| 用户 | 所属组 |
| --- | --- |
| `root` | `root`、`users` |
| `ubuntu` | `ubuntu`、`adm`、`dialout`、`cdrom`、`floppy`、`sudo`、`audio`、`dip`、`video`、`plugdev` |
| `user` | `user`、`sudo`、`users` |
| `dockremap` | `dockremap` |
| `nova` | `nova` |
| `sync` | `nogroup` |

`/etc/sudoers` 中的关键规则为：

```sudoers
root ALL=(ALL:ALL) ALL
%sudo ALL=NOPASSWD:ALL
```

通过 `sudo -n -l -U ubuntu` 和 `sudo -n -l -U user` 核验，两个账号均获得：

```text
(root) NOPASSWD: ALL
```

因此，**仅把运行账号从 root 换成 ubuntu 或 user，并不能形成有效的低权限边界**。能够以这些账号执行命令的程序，仍可通过 sudo 获得容器内 root 权限。

`dockremap`、`nova`、`sync` 的 sudo 查询结果均为不允许执行 sudo。

## 独立 OpenSSH 的有效登录规则

主要配置如下：

```text
PermitRootLogin         yes
PasswordAuthentication  yes
PubkeyAuthentication    yes
KbdInteractiveAuthentication no
PermitEmptyPasswords    no
AuthenticationMethods   any
UsePAM                  yes
AuthorizedKeysCommand   none
TrustedUserCAKeys       none
ForceCommand            none
ChrootDirectory         none
```

授权公钥查找位置为：

```text
.ssh/authorized_keys .ssh/authorized_keys2
```

未发现 `AllowUsers`、`DenyUsers`、`AllowGroups`、`DenyGroups` 等账号访问规则，也未发现账号专属的 `Match` 配置。对上述账号进行的有效配置核查使用了连接端 `steam-os`、来源地址 `100.82.31.127`。

未发现 `/etc/nologin` 或 `/run/nologin` 登录阻断文件。

据此可作以下判断：

- **root：配置允许密码登录。** 本次没有尝试密码认证；实际访问还受网络可达性、PAM 等条件影响。
- **ubuntu、user、dockremap、nova：目前无法使用锁定的密码认证，也没有已配置的普通公钥登录凭证。**
- **密码锁定不等于账号被彻底禁用。** 平台执行机制或其他获授权认证渠道仍可能以该账号运行进程。
- **没有 SSH 用户白名单，不等于所有账号都能成功登录。** 认证凭证、Shell、账号状态和网络访问条件仍然影响登录结果。

## 其他本地系统账号

其余 21 个账号配置的是禁止登录或不可交互的 Shell，主要用于系统服务，不能视为正常 SSH 登录用户：

```text
daemon
bin
sys
games
man
lp
mail
news
uucp
proxy
www-data
backup
list
irc
_apt
nobody
systemd-network
messagebus
polkitd
pulse
sshd
```

本清单基于检查时的本地 `/etc/passwd`，不代表已经审核所有外部身份提供方或平台账号体系。

## 与 Tailscale SSH 的区别

当前通过 `100.120.78.38` 使用的管理连接由 **Tailscale SSH** 处理，其授权来自尾网 SSH 策略，不依赖上述 OpenSSH 的 `authorized_keys` 文件。

因此，root 没有授权公钥，与当前仍能通过 Tailscale SSH 登录并不矛盾。

独立 OpenSSH 与 Tailscale SSH 的授权规则需要分别管理：修改 OpenSSH 的 `PermitRootLogin` 或其他认证选项，不能替代调整 Tailscale SSH 策略。本次没有读取尾网管理控制台策略，因此不能列出所有可通过 Tailscale 登录的身份与系统账号映射。

## 容器与宿主机的权限边界

上述权限均属于**执行容器内部**。检查到的用户命名空间映射为：

```text
         0     100000      65536
```

即容器 UID 0 映射到上层 UID 100000，映射范围为 65536 个 UID。**容器 root 不能直接等同于腾讯云 CVM 宿主机 root。**

## 核验方法与限制

主要使用的只读检查包括：

- `/etc/passwd`：本地账号、UID、主目录与 Shell。
- `id 用户名`：组成员关系。
- `passwd -S 用户名`：密码状态标记。
- `sudo -n -l -U 用户名`：有效 sudo 授权。
- `sshd -T -C ...`：指定账号和来源条件下的有效 SSH 配置。
- SSH 配置及包含文件：用户访问规则和 Match 条件。
- 授权公钥文件存在性检查：未输出公钥正文或注释。
- `/proc/self/uid_map`：用户命名空间映射。

本结果是 2026 年 11 月 10 日 16:57 的配置快照。没有进行密码强度测试、实际密码登录测试、完整权限提升测试或宿主机权限检查。
