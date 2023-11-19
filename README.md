# FreeKill-Web-Panel (FKWP)

### A web control panel for server side [FreeKill](https://github.com/Qsgs-Fans/FreeKill/), depends on [Flask](https://github.com/pallets/flask) and [tmux](https://github.com/tmux/tmux)

![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/shadlc/FreeKill-Web-Panel)
![GitHub Lines of code](https://img.shields.io/tokei/lines/github/shadlc/FreeKill-Web-Panel)
![GitHub repo size](https://img.shields.io/github/repo-size/shadlc/FreeKill-Web-Panel)
![GitHub - License](https://img.shields.io/github/license/shadlc/FreeKill-Web-Panel)
![platform](https://img.shields.io/badge/platform-linux-blue)
![GitHub last commit](https://img.shields.io/github/last-commit/shadlc/FreeKill-Web-Panel)

## 💬 简介
**这是为Linux平台上，方便控制[新月杀](https://github.com/Qsgs-Fans/FreeKill/)而设计的零侵入网页管理面板，可以方便的管理与控制一个服务器上运行的一个或多个[新月杀](https://github.com/Qsgs-Fans/FreeKill/)服务端，同时与[新月杀](https://github.com/Qsgs-Fans/FreeKill/)服务端完全分离**

## ✨ 主要功能

- **创建、启动、停止新月杀服务器**
- **监控新月杀服务器运行状态**
- **网页操作新月杀服务器终端**
- ~~**一键更新新月杀服务器**~~ (TODO)
- ~~**修改月杀服务器参数与配置**~~ (TODO)
- ~~**前端展示玩家列表、房间列表、扩展包列表**~~ (TODO)

## 📸 相关截图

<div align=center>
<img src="https://github.com/shadlc/FreeKill-Web-Panel/assets/46913095/9c075b65-ca20-4cc1-adb6-f43215fca346" width=70%>
</div>


## 📝 使用指南
- **首先确保你安装了 Python3.11、tmux、git**
- **本项目使用了 pipenv 依靠虚拟环境进行依赖项管理，请使用 pip install pipenv 安装模块之后启动**
- **本项目只是一个管理面板，没有提供任何[新月杀](https://github.com/Qsgs-Fans/FreeKill/)配置或安装功能，请自行准备可以正常启动的新月杀路径**
- **本项目没有安全验证系统，请自行增加鉴权模块‼️‼️‼️注意，直接暴露在公网上是极其危险的行为‼️‼️‼️**
- **启动步骤**
  1. 执行 `git clone https://github.com/shadlc/FreeKill-Web-Panel.git`
  2. 执行 `cd FreeKill-Web-Panel/`
  3. 执行 `chmod +x start.sh`
  4. 执行 `sh start.sh`
  5. 使用任意反向代理软件代理本机9500端口到目标路径
  6. 打开网页并使用


## 🔒️ 许可协议
- 本项目在遵循 [**GNU GENERAL PUBLIC LICENSE v3.0**](https://www.gnu.org/licenses/gpl-3.0.html) 许可协议下进行发布

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=shadlc/FreeKill-Web-Panel&type=Date)](https://star-history.com/#shadlc/FreeKill-Web-Panel)
