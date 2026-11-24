#!/usr/bin/env python3
"""Replace hardcoded UI string literals in Cursor workbench bundles.

React/UI property values are rewritten, along with the settings sidebar
label map (those titles are not stored as component properties). Backups
are stored next to the originals as <file>.cursor-zh.bak and can be restored.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROPS = (
    "children",
    "title",
    "placeholder",
    "aria-label",
    "ariaLabel",
    "label",
    "description",
    "tooltip",
    "heading",
    "subtitle",
    "emptyText",
    "confirmText",
    "cancelText",
    "buttonText",
    "helperText",
    "errorText",
    "pageTitle",
    "collectionLabel",
    "projectAgentsSectionLabel",
)
PROP_RE = re.compile(
    r"(?P<prop>" + "|".join(PROPS) + r"):\"(?P<text>(?:[^\"\\]|\\.)*)\""
)
# Quoted strings that only appear as display text. "VS Code Settings" also
# appears as an nls `original:` source and must be left unchanged.
SAFE_QUOTED = (
    "Search Settings",
    "Search settings",
    "Code Intelligence",
    "Browser & Network",
    "Plan & Usage",
    "Tools & MCPs",
    "Rules, Skills, Subagents",
    "Worktrees",
    "Contact",
    "Loading settings",
    "VS Code Settings",
    "New Chat",
    "New Project",
    "Send follow-up",
    "Follow up",
    "This Mac",
    "This PC",
    "This Computer",
    "Side Chat",
    "New Side Chat",
    "Side Chats",
    "Add to Side Chat",
    "Move to Side Chat",
    "Open Side Chat",
    "Split Down",
    "Split Right",
)
NAV_VALUE_RE = re.compile(
    r'(?P<key>"(?:[^"\\]|\\.)*"|[A-Za-z_][\w-]*):"(?P<text>(?:[^"\\]|\\.)*)"'
)
NAV_ANCHOR = '"plan-usage":"'
DEFAULT_APP = Path("/Applications/Cursor.app/Contents/Resources/app/out/vs/workbench")
BUNDLES = (
    "workbench.glass.main.js",
    "workbench.desktop.main.js",
    "workbench.anysphere-ui-automations.js",
    "workbench.xai-commerce-prepaid.js",
)


def js_string(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def load_dict(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must be a JSON object of english -> chinese")
    return {str(key): str(value) for key, value in data.items() if key != value}


def decode_js_string(raw: str) -> str | None:
    try:
        return json.loads('"' + raw + '"')
    except json.JSONDecodeError:
        return None


def patch_text(text: str, mapping: dict[str, str]) -> tuple[str, int]:
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        decoded = decode_js_string(match.group("text"))
        if decoded is None:
            return match.group(0)
        translated = mapping.get(decoded)
        if translated is None:
            return match.group(0)
        count += 1
        return f"{match.group('prop')}:{js_string(translated)}"

    text = PROP_RE.sub(replace, text)
    text, panel_count = patch_workspace_panel(text)
    extra, extra_count = patch_settings_labels(text, mapping)
    count += panel_count
    extra, remote_count = patch_remote_control_copy(extra)
    return extra, count + extra_count + remote_count


def patch_settings_labels(text: str, mapping: dict[str, str]) -> tuple[str, int]:
    count = 0
    text, nav_count = patch_settings_nav(text, mapping)
    count += nav_count
    text, footer_count = patch_settings_footer(text, mapping)
    count += footer_count
    text, quoted_count = patch_safe_quoted(text, mapping)
    count += quoted_count
    return text, count


def patch_settings_nav(text: str, mapping: dict[str, str]) -> tuple[str, int]:
    count = 0
    start = 0
    while True:
        anchor = text.find(NAV_ANCHOR, start)
        if anchor < 0:
            break
        brace = text.rfind("{", max(0, anchor - 400), anchor)
        if brace < 0:
            start = anchor + len(NAV_ANCHOR)
            continue
        end = _matching_brace(text, brace)
        if end is None:
            start = anchor + len(NAV_ANCHOR)
            continue
        obj = text[brace:end]
        # Icon-name maps use the same keys. Only the label map has display titles.
        if '"background-composer"' not in obj or ':"General"' not in obj:
            start = anchor + len(NAV_ANCHOR)
            continue
        rewritten, replaced = _translate_object_values(obj, mapping)
        if replaced:
            text = text[:brace] + rewritten + text[end:]
            count += replaced
            start = brace + len(rewritten)
        else:
            start = end
    return text, count


def _matching_brace(text: str, open_at: int) -> int | None:
    depth = 0
    limit = min(len(text), open_at + 4000)
    for index in range(open_at, limit):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index + 1
    return None


def _translate_object_values(obj: str, mapping: dict[str, str]) -> tuple[str, int]:
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        decoded = decode_js_string(match.group("text"))
        if decoded is None:
            return match.group(0)
        translated = mapping.get(decoded)
        if translated is None:
            return match.group(0)
        count += 1
        return f"{match.group('key')}:{js_string(translated)}"

    return NAV_VALUE_RE.sub(replace, obj), count


def patch_settings_footer(text: str, mapping: dict[str, str]) -> tuple[str, int]:
    docs = mapping.get("Docs")
    contact = mapping.get("Contact")
    if docs is None or contact is None:
        return text, 0
    old = '{docs:"Docs",contact:"Contact"}'
    new = "{docs:" + js_string(docs) + ",contact:" + js_string(contact) + "}"
    count = text.count(old)
    if count == 0:
        return text, 0
    return text.replace(old, new), count


def patch_safe_quoted(text: str, mapping: dict[str, str]) -> tuple[str, int]:
    count = 0
    for phrase in SAFE_QUOTED:
        translated = mapping.get(phrase)
        if translated is None:
            continue
        source = js_string(phrase)
        pattern = re.compile(r"(?<!original:)" + re.escape(source))
        text, replaced = pattern.subn(js_string(translated), text)
        count += replaced

    search = mapping.get("Search settings")
    if search is not None:
        old = "`Search settings ${"
        new = "`" + search + " ${"
        found = text.count(old)
        if found:
            text = text.replace(old, new)
            count += found

    results_old = "${F.length} results"
    results_new = "${F.length} 个结果"
    found = text.count(results_old)
    if found:
        text = text.replace(results_old, results_new)
        count += found

    prefix_old = "Cursor Settings: "
    prefix_new = "Cursor 设置："
    found = text.count(prefix_old)
    if found:
        text = text.replace(prefix_old, prefix_new)
        count += found

    back = mapping.get("Back")
    if back is not None:
        rendered = js_string(back)
        for source in (
            '?"Back"',
            '??"Back"',
            'name:"Back"',
            'cancelLabel:"Back"',
            'textContent?.trim()==="Back"',
        ):
            target = source.replace('"Back"', rendered)
            found = text.count(source)
            if found:
                text = text.replace(source, target)
                count += found
    return text, count


# Display copy for the Remote Control settings page. These words also appear as
# identifiers elsewhere, so they are replaced only inside this copy module.
REMOTE_CONTROL_COPY = {
    "Not used yet": "尚未使用",
    "Last used just now": "刚刚使用",
    "1 device waiting for approval": "有 1 台设备等待批准",
    "This device": "此设备",
    "Requested just now": "刚刚请求",
    "Requested 1 minute ago": "1 分钟前请求",
    "Remote Control": "远程控制",
    "Allow agents on this computer to be controlled remotely from mobile": "允许从移动设备远程控制这台电脑上的智能体",
    "Turn Remote Control on again to reset this computer": "再次开启远程控制以重置这台电脑",
    "Control local agents on this computer from the Cursor iOS app.": "从 Cursor iOS 应用控制这台电脑上的本地智能体。",
    "This computer": "本机",
    "Other computers": "其他电脑",
    "Paired devices": "已配对设备",
    "No devices are currently paired with this computer.": "目前没有设备与这台电脑配对。",
    "Unnamed device": "未命名设备",
    "Disconnect\u2026": "断开连接\u2026",
    "Disconnect from this computer": "断开与这台电脑的连接",
    "It won\u2019t be able to control this computer until it\u2019s authorized here again.": "在此重新授权之前，它将无法控制这台电脑。",
    "Disconnect": "断开连接",
    "Disconnect from all computers": "断开与所有电脑的连接",
    "It won\u2019t be able to control any of your computers. To use it again, authorize it as a new device.": "它将无法控制你的任何电脑。要再次使用，请将其作为新设备授权。",
    "Remote Control runs on a cloud agent, which requires data storage that your current privacy mode disables": "远程控制依赖云端智能体，而你当前的隐私模式禁止了所需的数据存储",
    "Control local agents from your phone": "从手机控制本地智能体",
    "Start, check, and reply to agents running on this computer. Needs Cursor open and the computer awake.": "启动、查看并回复在这台电脑上运行的智能体。需要保持 Cursor 打开，且电脑处于唤醒状态。",
    "Keep this computer awake": "保持本机唤醒",
    "Stay connected to your phone while plugged in.": "接通电源时保持与手机的连接。",
    "Automatically register computers": "自动注册电脑",
    "Turn on Remote Control when you sign in on another computer.": "在另一台电脑上登录时开启远程控制。",
    "Disable on all of my computers": "在我的所有电脑上停用",
    "You can register again later.": "之后可以重新注册。",
    "Unregister all": "全部取消注册",
    "Disable Remote Control on all of your computers?": "要在你的所有电脑上停用远程控制吗？",
    "This will turn off Remote Control on every computer associated with your account.": "这将关闭你账户下每台电脑的远程控制。",
    "Couldn\u2019t unregister some computers. Try again.": "部分电脑未能取消注册。请重试。",
    "Computer name": "电脑名称",
    "How this computer appears in the iOS app.": "这台电脑在 iOS 应用中显示的名称。",
    "Self-Hosted Workers": "自托管 Worker",
    "Enable local self-hosted workers": "启用本地自托管 Worker",
    "Allow cloud agents to run in your local environment.": "允许云端智能体在你的本地环境中运行。",
    "Offline": "离线",
    "Connecting\u2026": "正在连接\u2026",
    "Connected": "已连接",
    "Check clock": "检查时钟",
    "Another window": "另一窗口",
    "Remote Control is running in another Cursor window": "远程控制正在另一个 Cursor 窗口中运行",
    "This computer\u2019s clock is wrong; set the date and time automatically to connect": "这台电脑的时钟不准。请将日期和时间设为自动设置后再连接",
    "Pair a device": "配对设备",
    "Scan with your iPhone camera to open Cursor and pair.": "用 iPhone 相机扫描，以打开 Cursor 并配对。",
    "Turn on Remote Control to show a code.": "开启远程控制以显示配对码。",
    "Turn On Remote Control": "开启远程控制",
    "Turning on Remote Control\u2026": "正在开启远程控制\u2026",
    "Preparing a code\u2026": "正在准备配对码\u2026",
    "Remote Control is on in another Cursor window.": "远程控制已在另一个 Cursor 窗口中开启。",
    "Copy Link": "复制链接",
    "Copied": "已复制",
    "Don\u2019t have the app?": "还没有这个应用？",
    "Get it on the App Store": "前往 App Store 获取",
    "New Code": "新配对码",
    "Device paired": "设备已配对",
    "Couldn\u2019t pair": "无法配对",
    "Get a new code and scan it again.": "获取新配对码后重新扫描。",
    "Allowing\u2026": "正在允许\u2026",
    "Done": "完成",
    "Go to Remote Control settings": "前往远程控制设置",
    "Pair another device": "配对另一台设备",
    "No devices paired yet": "尚未配对设备",
    "Scan a QR code with your iPhone camera to pair.": "用 iPhone 相机扫描二维码进行配对。",
    "Allow this device?": "允许此设备？",
    "Allow": "允许",
    "Don\u2019t allow": "不允许",
    "It will be able to start, check, and reply to agents on this computer. Only allow it if your device shows this code:": "它将能够在这台电脑上启动、查看并回复智能体。仅当你的设备显示此代码时才允许：",
}
REMOTE_CONTROL_TEMPLATES = (
    ("`Last used ${Ine(t.lastUsedAtMs,!0)}`", "`上次使用 ${Ine(t.lastUsedAtMs,!0)}`"),
    ("`${t.count} devices waiting for approval`", "`${t.count} 台设备等待批准`"),
    ("} can now control agents on this computer.`", "} 现在可以控制这台电脑上的智能体。`"),
    ("`Requested ${e} minutes ago`", "`${e} 分钟前请求`"),
    ("`Allow \\u201C${t}\\u201D?`", "`允许\\u201C${t}\\u201D?`"),
)
REMOTE_QUOTED = re.compile(r'"(?:[^"\\]|\\.)*"')


def patch_remote_control_copy(text: str) -> tuple[str, int]:
    start = text.find('"Not used yet"')
    marker = "Only allow it if your device shows this code:"
    end_at = text.find(marker)
    if start < 0 or end_at < start:
        return text, 0
    end = text.find('"', end_at + len(marker))
    if end < 0:
        return text, 0
    end += 1
    region = text[start:end]
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        try:
            decoded = json.loads(match.group(0))
        except json.JSONDecodeError:
            return match.group(0)
        translated = REMOTE_CONTROL_COPY.get(decoded)
        if translated is None:
            return match.group(0)
        count += 1
        return js_string(translated)

    region = REMOTE_QUOTED.sub(replace, region)
    for old, new in REMOTE_CONTROL_TEMPLATES:
        found = region.count(old)
        if found:
            region = region.replace(old, new)
            count += found
    return text[:start] + region + text[end:], count


PANEL_EXACT = (
    (
        'function uRu(t){switch(t){case $t.Terminal:return"Terminal";case $t.Browser:return"Browser";case $t.File:return"File";case $t.AgentFiles:return"Files";case $t.Gallery:return"Gallery";case $t.ColorReference:return"Colors";case $t.Plan:return"Plan";case $t.EnvironmentSetup:return"Environment";case $t.SideChat:return"Side Chat";case $t.Vnc:case $t.AgentVnc:return"Desktop";case $t.Diff:case $t.AgentChanges:return"Changes";case $t.Output:return"Output";case $t.Pr:return"Pull Request";case $t.Canvas:return"Canvas";case $t.Context:return lte.label;case $t.MainBotTasks:return DAe.label;case $t.PrIndex:return V1e.label;case $t.AgentContext:return rWe.label;case $t.Machine:return"Machine Metrics";case $t.VoiceCallTranscript:return"Voice chat";default:return"Tab"}}',
        'function uRu(t){switch(t){case $t.Terminal:return"终端";case $t.Browser:return"浏览器";case $t.File:return"文件";case $t.AgentFiles:return"文件";case $t.Gallery:return"图库";case $t.ColorReference:return"颜色";case $t.Plan:return"计划";case $t.EnvironmentSetup:return"环境";case $t.SideChat:return"侧边聊天";case $t.Vnc:case $t.AgentVnc:return"桌面";case $t.Diff:case $t.AgentChanges:return"更改";case $t.Output:return"输出";case $t.Pr:return"拉取请求";case $t.Canvas:return"画布";case $t.Context:return lte.label;case $t.MainBotTasks:return DAe.label;case $t.PrIndex:return V1e.label;case $t.AgentContext:return rWe.label;case $t.Machine:return"机器指标";case $t.VoiceCallTranscript:return"语音聊天";default:return"标签页"}}',
    ),
    (
        'function HF3(t){return t<=0?"Terminal":t===1?"1 Terminal":`${t} Terminals`}',
        'function HF3(t){return t<=0?"终端":t===1?"1 个终端":`${t} 个终端`}',
    ),
    (
        'sectionHeaderLabel:`On ${t.workspaceName.trim()||"workspace"}`',
        'sectionHeaderLabel:`在 ${t.workspaceName.trim()||"工作区"}`',
    ),
    ('||"Pull Request"', '||"拉取请求"'),
    ('?"Unpin":"Pin"', '?"取消固定":"固定"'),
    ('?"Mark as Read":"Mark as Unread"', '?"标记为已读":"标为未读"'),
    (
        'function UFE(t){switch(t){case"agents":return"Search chats...";case"files":return"Search files...";case"all":return"Search chats, files, and actions..."}}',
        'function UFE(t){switch(t){case"agents":return"搜索聊天...";case"files":return"搜索文件...";case"all":return"搜索聊天、文件和操作..."}}',
    ),
    (
        'v70={all:"All",agents:"Chats",files:"Files"}',
        'v70={all:"全部",agents:"聊天",files:"文件"}',
    ),
    ('Wr="Chats"', 'Wr="聊天"'),
    (
        'h6v=["Agent","Mode","Workspace","View","Settings","Appearance","Developer"]',
        'h6v=["智能体","模式","工作区","视图","设置","外观","开发人员"]',
    ),
    ('glassCategory:"Agent"', 'glassCategory:"智能体"'),
    ('glassCategory:"Mode"', 'glassCategory:"模式"'),
    ('glassCategory:"Workspace"', 'glassCategory:"工作区"'),
    ('glassCategory:"View"', 'glassCategory:"视图"'),
    ('glassCategory:"Settings"', 'glassCategory:"设置"'),
    ('glassCategory:"Appearance"', 'glassCategory:"外观"'),
    ('glassCategory:"Developer"', 'glassCategory:"开发人员"'),
    ('B==="Workspace"', 'B==="工作区"'),
    ('heading:"Suggested"', 'heading:"建议"'),
    ('heading:"Workspace"', 'heading:"工作区"'),
)


def patch_workspace_panel(text: str) -> tuple[str, int]:
    count = 0
    for old, new in PANEL_EXACT:
        found = text.count(old)
        if found:
            text = text.replace(old, new)
            count += found
    for old, new in (('||"Terminal"', '||"终端"'), ('?"Terminal"', '?"终端"')):
        found = text.count(old)
        if found:
            text = text.replace(old, new)
            count += found
    return text, count


def check_syntax(path: Path) -> None:
    subprocess.run(["node", "--check", str(path)], check=True)


def restore(directory: Path) -> None:
    restored = 0
    for name in BUNDLES:
        backup = directory / f"{name}.cursor-zh.bak"
        target = directory / name
        if backup.exists():
            shutil.copy2(backup, target)
            restored += 1
    print(f"restored {restored} bundles")


def install(directory: Path, mapping: dict[str, str]) -> None:
    total = 0
    for name in BUNDLES:
        target = directory / name
        if not target.exists():
            print(f"skip missing {target}")
            continue
        backup = directory / f"{name}.cursor-zh.bak"
        if not backup.exists():
            shutil.copy2(target, backup)
        original = backup.read_text(encoding="utf-8")
        patched, count = patch_text(original, mapping)
        if count == 0:
            print(f"{name}: no replacements")
            continue
        target.write_text(patched, encoding="utf-8")
        check_syntax(target)
        total += count
        print(f"{name}: {count} replacements")
    print(f"patched {total} UI strings")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dict", type=Path, required=False)
    parser.add_argument("--app", type=Path, default=DEFAULT_APP)
    parser.add_argument("--restore", action="store_true")
    args = parser.parse_args()
    if args.restore:
        restore(args.app)
        return
    if args.dict is None:
        raise SystemExit("--dict is required unless --restore is set")
    install(args.app, load_dict(args.dict))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
