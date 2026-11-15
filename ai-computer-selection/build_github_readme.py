"""Build a GitHub reading copy without changing the reviewed local Markdown."""
from pathlib import Path
from urllib.parse import quote
import re

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPOSITORY = "https://github.com/raoliaoyuan/CloudedPC/blob/main/"
SOURCE = BASE / "document/AI执行环境选择流程说明与厂商系统对比.md"
LOCAL_PREFIX = "/home/gamer/Work/CloudPC/"


def github_link(match):
    relative = match.group(1)
    if not (ROOT / relative).is_file():
        raise FileNotFoundError(relative)
    suffix = "?raw=true" if relative.endswith(".png") else ""
    return "](" + REPOSITORY + quote(relative, safe="/") + suffix + ")"


source = SOURCE.read_text(encoding="utf-8")
body = re.sub(r"\]\(<?" + re.escape(LOCAL_PREFIX) + r"([^>\n)]+)>?\)", github_link, source)
body = body[:body.index("\n本地阅读说明：")].rstrip()
body += "\n\n本页由正式 Markdown 自动生成，仅将本机文件链接转换为 GitHub 链接；正文内容与最终复核版本相同。\n"
body += "\n## 文件与复核记录\n\n"
for title, relative in [
    ("正式 Markdown（供本地阅读）", "document/AI执行环境选择流程说明与厂商系统对比.md"),
    ("Claude CLI 最终复核报告", "document/review/Claude-CLI-最终复核报告.md"),
    ("流程图生成脚本", "build_diagram.py"),
]:
    body += f"- [{title}]({REPOSITORY}{quote('ai-computer-selection/' + relative, safe='/')})\n"
body += "\n`document` 中的 Word、PDF、QA 图片、评审前副本及转换脚本是历史过程材料；当前定稿以正式 Markdown、顶层 PNG 与 Draw.io 为准。请勿用早期 Word 转换脚本覆盖定稿 Markdown。\n"
(BASE / "README.md").write_text(body, encoding="utf-8")
print("Created GitHub reading copy:", BASE / "README.md")
