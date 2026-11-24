# Cursor 简体中文

把 Cursor 界面换成简体中文。翻译基于 VS Code 官方简体中文语言包，并补上 Cursor 3.31 自己的界面文案。

VS Code 部分的译文来自 [microsoft/vscode-loc](https://github.com/microsoft/vscode-loc)。这是社区项目，与 Anysphere、微软没有隶属关系。

安装会改两处：

- 已安装的简体中文语言包（菜单、设置，以及走翻译系统的 Cursor 文案）
- Cursor 安装目录里的界面脚本（按钮、标题、占位符等写死的英文）

改安装目录前请先完全退出 Cursor。Cursor 更新后，安装目录里的替换会被覆盖，需要再做一次第 4 步和第 5 步。

## 从扩展商店安装语言包

在 Cursor 扩展视图搜索 `zyan.cursor-zh`，安装 **Chinese (Simplified) (简体中文) Language Pack for Cursor**（发布者 `zyan`）。

然后：

1. 卸掉或禁用官方 **Chinese (Simplified) Language Pack**（发布者 `MS-CEINTL`）。两个语言包都提供简体中文时，重启后用哪一套译文不确定。
2. 按 `Command+Shift+P`（Windows / Linux 用 `Ctrl+Shift+P`）打开命令面板，运行 **Configure Display Language**，选择 **中文(简体)**。
3. 完全退出 Cursor 再打开。只重载窗口不够。

商店里还没有这一项时，打开 [Releases](https://github.com/aa24615/cursor-zh/releases)，下载 `.vsix`。命令面板运行 **Extensions: Install from VSIX...**，选中该文件。

商店语言包只覆盖走翻译系统的文案。按钮、标题、占位符等写死的英文仍要做第 4 步和第 5 步。用商店或 VSIX 安装时，可以跳过第 1 步到第 3 步。

## 环境

- Cursor 3.31 附近的版本。其它版本可能还有英文残留。
- Python 3
- 命令行里能运行 `node`（补丁写入后会做语法检查）

## 1. 安装官方简体中文语言包

在 Cursor 扩展里搜索并安装 **Chinese (Simplified) Language Pack**（发布者 `MS-CEINTL`）。

装好后完全退出 Cursor（macOS 用 `Command+Q`）。只重载窗口不够。

## 2. 换上本仓库的语言包译文

找到已安装的语言包目录，名字类似：

| 系统 | 目录 |
| --- | --- |
| macOS / Linux | `~/.cursor/extensions/ms-ceintl.vscode-language-pack-zh-hans-<版本>-universal` |
| Windows | `%USERPROFILE%\.cursor\extensions\ms-ceintl.vscode-language-pack-zh-hans-<版本>-universal` |

备份后，用本仓库的文件覆盖里面的 `translations/main.i18n.json`。

macOS / Linux：

```bash
EXT=$(echo "$HOME/.cursor/extensions"/ms-ceintl.vscode-language-pack-zh-hans-*-universal | awk '{print $1}')
cp "$EXT/translations/main.i18n.json" "$EXT/translations/main.i18n.json.cursor-zh.bak"
cp i18n/vscode-language-pack-zh-hans/translations/main.i18n.json "$EXT/translations/main.i18n.json"
```

Windows PowerShell：

```powershell
$ext = Get-ChildItem "$env:USERPROFILE\.cursor\extensions" -Directory -Filter "ms-ceintl.vscode-language-pack-zh-hans-*" | Select-Object -First 1
Copy-Item "$($ext.FullName)\translations\main.i18n.json" "$($ext.FullName)\translations\main.i18n.json.cursor-zh.bak"
Copy-Item "i18n\vscode-language-pack-zh-hans\translations\main.i18n.json" "$($ext.FullName)\translations\main.i18n.json"
```

命令在本仓库根目录执行。

## 3. 把显示语言设为简体中文

编辑 `argv.json`：

| 系统 | 文件 |
| --- | --- |
| macOS / Linux | `~/.cursor/argv.json` |
| Windows | `%USERPROFILE%\.cursor\argv.json` |

在 JSON 里加入或改成：

```json
"locale": "zh-cn"
```

保留文件里原有的 `crash-reporter-id` 等字段。

## 4. 替换写死在程序里的英文

补丁只改界面属性里的文字（例如按钮文字、标题、占位符），并在同目录生成 `.cursor-zh.bak`。已有备份时，会基于这份原始备份重新打补丁。

先确认下面的目录里有 `workbench.desktop.main.js`：

| 系统 | 工作台目录 |
| --- | --- |
| macOS | `/Applications/Cursor.app/Contents/Resources/app/out/vs/workbench` |
| Windows | `%LOCALAPPDATA%\Programs\Cursor\resources\app\out\vs\workbench` |
| Linux | `/usr/share/cursor/resources/app/out/vs/workbench`，也可能在 `~/.local/share/cursor` 或 `/opt/Cursor` |

macOS 可以直接运行：

```bash
python3 scripts/patch_hardcoded.py --dict build/hardcoded-zh.json
```

Windows / Linux 加上实际目录：

```bash
python3 scripts/patch_hardcoded.py --dict build/hardcoded-zh.json --app "工作台目录"
```

结束时应看到各文件的替换数量。若提示找不到 `node`，先安装 Node.js 18 或更高版本，再重新执行。

## 5. 更新校验和

Cursor 会核对 `workbench.desktop.main.js`。不更新校验和时，启动可能提示安装文件已损坏。

在仓库根目录执行（把 `APP` 换成你的 `resources/app` 目录）：

```bash
python3 - << 'PY'
import base64, hashlib, shutil
from pathlib import Path

# macOS 默认路径。Windows / Linux 改成自己的 resources/app 目录。
app = Path("/Applications/Cursor.app/Contents/Resources/app")
product = app / "product.json"
js = app / "out/vs/workbench/workbench.desktop.main.js"
backup = product.with_name("product.json.cursor-zh.bak")
if not backup.exists():
    shutil.copy2(product, backup)
digest = base64.b64encode(hashlib.sha256(js.read_bytes()).digest()).decode().rstrip("=")
text = product.read_text(encoding="utf-8")
old = text.split('"vs/workbench/workbench.desktop.main.js": "', 1)[1].split('"', 1)[0]
product.write_text(text.replace(old, digest, 1), encoding="utf-8")
print("checksum", digest)
PY
```

Windows 示例：

```python
app = Path(r"C:\Users\你的用户名\AppData\Local\Programs\Cursor\resources\app")
```

## 6. 重新打开 Cursor

再次完全退出后重新打开。界面应显示为简体中文。

Cursor、Git、GitHub、MCP、SSH 等产品名保持英文。代码、终端内容和 AI 回复不会被翻译。

## 恢复英文界面

先完全退出 Cursor，再在仓库根目录执行。

恢复程序文件：

```bash
python3 scripts/patch_hardcoded.py --restore
```

其它系统加上 `--app "工作台目录"`。

恢复校验和：

```bash
cp "/Applications/Cursor.app/Contents/Resources/app/product.json.cursor-zh.bak" \
   "/Applications/Cursor.app/Contents/Resources/app/product.json"
```

恢复语言包时，把第 2 步生成的 `main.i18n.json.cursor-zh.bak` 拷回 `main.i18n.json`。显示语言可在 `argv.json` 里删掉 `locale`，或改成 `en`。

## 来源与许可

VS Code 界面译文来自 [microsoft/vscode-loc](https://github.com/microsoft/vscode-loc)，许可见 [LICENSE.md](LICENSE.md)。Cursor 专有文案在此基础上补充。
