"""Build a GitHub reading copy without changing the reviewed local Markdown."""
from pathlib import Path
from urllib.parse import quote
import re
import os

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPOSITORY = "https://github.com/raoliaoyuan/CloudedPC/blob/main/"
SOURCE = BASE / "document/AI执行环境选择流程说明与厂商系统对比.md"
LOCAL_PREFIX = "/home/gamer/Work/CloudPC/"


def github_link(match):
    label = match.group(1)
    href = match.group(2) or match.group(3)
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", href) or href.startswith("#"):
        return match.group(0)
    target = ((ROOT / href[len(LOCAL_PREFIX):]) if href.startswith(LOCAL_PREFIX)
              else (SOURCE.parent / href)).resolve()
    relative = target.relative_to(ROOT).as_posix()
    if not target.is_file():
        raise FileNotFoundError(relative)
    # Repository-relative images let GitHub resolve private-repository access.
    destination = (quote(os.path.relpath(target, BASE), safe="/") if label.startswith("!")
                   else REPOSITORY + quote(relative, safe="/"))
    return label + "(" + destination + ")"


source = SOURCE.read_text(encoding="utf-8")
body = re.sub(r"(!?\[[^\]\n]*\])\((?:<([^>\n]+)>|([^\s)\n]+))\)", github_link, source)
body = body[:body.index("\n文件路径说明：")].rstrip()
body += "\n\n本页由正式 Markdown 自动生成，适配文件与图片链接并补充导航；判断逻辑与报告结论沿用最终复核版本。\n"
body += "\n## 文件与复核记录\n\n"
for title, relative in [
    ("正式 Markdown（支持 GitHub 与本地阅读）", "document/AI执行环境选择流程说明与厂商系统对比.md"),
    ("Claude CLI 最终复核报告", "document/review/Claude-CLI-最终复核报告.md"),
    ("流程图生成脚本", "build_diagram.py"),
]:
    body += f"- [{title}]({REPOSITORY}{quote('ai-computer-selection/' + relative, safe='/')})\n"
body += "\n`document` 中的 Word、PDF、QA 图片、评审前副本及转换脚本是历史过程材料；当前定稿以正式 Markdown、顶层 PNG 与 Draw.io 为准。请勿用早期 Word 转换脚本覆盖定稿 Markdown。\n"
(BASE / "README.md").write_text(body, encoding="utf-8")
print("Created GitHub reading copy:", BASE / "README.md")
