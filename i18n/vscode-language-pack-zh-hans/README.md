# Cursor 全量汉化

Cursor 简体中文，覆盖 **IDE** 和 **Agent**。

- **IDE**：编辑器菜单、命令面板、设置、源代码管理、终端，以及 Cursor 写在 IDE 里的设置页。
- **Agent**：智能体侧栏、对话输入栏、搜索、右键菜单、工作区面板、远程控制和运行模式。

VS Code 部分的译文来自 [microsoft/vscode-loc](https://github.com/microsoft/vscode-loc)。语言包负责走翻译系统的文案。按钮、标题、占位符等写死的英文要按仓库说明再打补丁，两步都做完才是全量汉化：https://github.com/aa24615/cursor-zh

## 已汉化的页面

### IDE

- 编辑器菜单、命令面板、源代码管理、终端、调试
- 设置侧栏：通用、外观、计划与用量、智能体、远程控制、云端智能体、模型、语音、源代码管理、浏览器和网络、代码智能、测试版、文档
- 设置内容：规则、技能、子智能体，工具与 MCP，工作树

### Agent

- 智能体侧栏：新建聊天、自动化、项目、新建项目、工作区
- 远程控制，对话输入栏，工作区面板（文件、更改、终端、浏览器、画布、侧边聊天）
- 右键菜单：拆分、固定、重命名、未读、复制、归档、分享
- 搜索聊天、文件和操作
- 执行与审批里的运行模式、允许列表、沙箱、自动审查

Cursor、Git、GitHub、MCP、SSH 等产品名保持英文。代码、终端输出和 AI 回复不会被翻译。

## 从扩展商店安装

1. 在 Cursor 扩展视图搜索 `zyan.cursor-zh`，安装本语言包。
2. 卸掉或禁用官方 **Chinese (Simplified) Language Pack**（发布者 `MS-CEINTL`）。两个语言包都提供简体中文时，重启后用哪一套译文不确定。
3. 按 `Ctrl+Shift+P`（macOS 为 `Command+Shift+P`）打开命令面板，运行 **Configure Display Language**。
4. 选择 **中文(简体)**（`zh-cn`）。
5. 完全退出 Cursor 后重新打开。只重载窗口不够。

没有商店条目时，从 [Releases](https://github.com/aa24615/cursor-zh/releases) 下载 `.vsix`，命令面板运行 **Extensions: Install from VSIX...** 安装，再从第 3 步继续。

按钮、标题、占位符等写死在程序里的英文不在语言包里。这部分按仓库说明再打一次补丁：https://github.com/aa24615/cursor-zh

## 参与

有关翻译改进的反馈，请在 [vscode-loc](https://github.com/microsoft/vscode-loc) 存储库中创建问题。
翻译字符串在 Microsoft 本地化平台中维护。只能在 Microsoft 本地化平台中进行更改，然后才能导出到 vscode-loc 存储库。因此，vscode-loc 存储库中不接受拉取请求。

## 许可证

源代码和字符串使用[MIT](https://github.com/Microsoft/vscode-loc/blob/master/LICENSE.md)许可进行授权。

## 感谢

此中文（简体）语言包是“来自社区，奉献社区”的社区本地化工作的成果。

特别感谢社区中每一位向这个项目做出贡献的朋友。

**杰出贡献者：**

* Joel Yang：在此项目向社区开放之后，翻译了大部分新增字符串。先后翻译了4万余字。
* Daniel Ye
* Neng Xue

**贡献者：**

* YF
* 陈嘉恺
* pluwen
* Shawn Dai
* Ying Feng
* Simon Chan
* 王子实
* 王韦煊
* 王旭晨
* Zijian Zhou
* wwj403
* Shizeng Zhou
* Aifen Qin
* lychichem
* Wang Dongcheng
* Yurui Zhang
* DongWei
* Bingxing Wang
* 林昊
* KingofCoding
* 潘冬冬
* 陈仁松
* Henry Chu
* Zhijian Zeng
* aimin guo
* 刘丁明
* hackereric
* Zou Jian
* Jianfeng Fang
* Ricky Wang
* Egg Zhang

**尽情享用吧！**

#  Chinese (Simplified) Language Pack for VS Code

Chinese (Simplified) Language Pack provides localized UI experience for VS Code.

## Usage

You can override the default UI language by explicitly setting the VS Code display language using the **Configure Display Language** command.

Press `Ctrl+Shift+P` to bring up the **Command Palette** then start typing `display` to filter and display the **Configure Display Language** command.

Press `Enter` and a list of installed languages by locale is displayed, with the current locale highlighted. Select another `locale` to switch UI language.

See [Docs](https://go.microsoft.com/fwlink/?LinkId=761051) for more information.

## Contributing

For feedback of translation improvement, please create Issue in [vscode-loc](https://github.com/microsoft/vscode-loc) repo.

The translation strings are maintained in Microsoft Localization Platform. Change can only be made in Microsoft Localization Platform then export to vscode-loc repo. So pull request won't be accepted in vscode-loc repo.

## License

The source code and strings are licensed under the [MIT](https://github.com/Microsoft/vscode-loc/blob/master/LICENSE.md) license.

## Credits

Chinese (Simplified) Language Pack had received contribution through "By the community, for the community" community localization effort.

Special thanks to community contributors for making it available.

**Top Contributors:**

* Joel Yang: localized majority of the new translation volume since open the project to community. Total 40k words localized.

**Contributors:**

* YF
* 陈嘉恺
* pluwen
* Shawn Dai
* Ying Feng
* Simon Chan
* 王子实
* 王韦煊
* Zijian Zhou
* wwj403
* Shizeng Zhou
* Aifen Qin
* lychichem
* Wang Dongcheng
* Yurui Zhang
* DongWei
* Bingxing Wang
* 林昊
* KingofCoding
* 潘冬冬
* 陈仁松
* Henry Chu
* Zhijian Zeng
* aimin guo
* 刘丁明
* hackereric
* Zou Jian
* Jianfeng Fang
* Ricky Wang
* Egg Zhang

**Enjoy!**
