# FreeKill-Web-Panel (FKWP)

### A web control panel for server side [FreeKill](https://github.com/Qsgs-Fans/FreeKill/), depends on [Flask](https://github.com/pallets/flask)

![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/shadlc/FreeKill-Web-Panel)
![Scc Count Badge](https://sloc.xyz/github/shadlc/FreeKill-Web-Panel)
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
- **一键更新新月杀服务器**
- **修改月杀服务器参数与配置**
- **前端展示玩家列表、房间列表、扩展包列表**


## 📸 相关截图

<div align=center>
<img src="https://github.com/shadlc/FreeKill-Web-Panel/assets/46913095/9c075b65-ca20-4cc1-adb6-f43215fca346" width=70%>
</div>
<div align=center>
<img src="https://github.com/shadlc/FreeKill-Web-Panel/assets/46913095/a1b45e02-af14-467b-b090-e4802b9ab551" width=70%>
</div>


## 📝 使用指南

### 启动步骤
- **首先确保你安装了 Python3.11、git、(tmux或者screen)**
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

### 配置说明
- **`host`决定了本程序监听的地址，默认为`127.0.0.1`，也就是只允许本机访问**
- **`port`是本程序监听的地址，默认为`9500`**
- **`log_file`为新月杀终端交互读取临时日志文件名，默认为`fk-latest.log`**
- **`version_check_url`为程序检测新月杀是否有新版本更新的网址，默认地址为[https://gitee.com/notify-ctrl/FreeKill/releases/latest](https://gitee.com/notify-ctrl/FreeKill/releases/latest)，原理是使用latest标签会自动进行302跳转到最新tag的release地址**
- **`backup_directory`是本程序备份包路径，默认为`backups`，可使用相对路径或绝对路径**
- **`backup_ignore`是备份时忽略的文件或文件夹列表，默认为忽略`.git`、`.github`、`build`，备份包文件夹路径自动排除**
- **`custom_trans`为自定义翻译表，当读取新月杀扩充包时，其未对某个值进行翻译时，会以此字典作为全局基础翻译表，如果该值已被翻译表处理过，则无效**
- **`server_dict`是由本程序接管启动的服务器列表，默认为空，原则上不应手动修改，本程序会将变动实时写入**

### 反向代理设置
- **本项目使用的Socket.io基于WebSocket，需单独设置请求头"Connection"为"upgrade"，且无法使用子目录**
- **下面是示例**

#### NGINX
- **使用该配置即可在 http://example.com:9501 正常地访问FKWP**
- **需要注意的是，必须正确配置auth_basic用户名与密码，比如使用工具htpasswd确保安全地访问**
```
server {
  listen 9501;
  server_name example.com;
  auth_basic on;
  auth_basic_user_file /var/www/auth_basic_user_file;

  location / {
    proxy_pass http://127.0.0.1:9500/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-Host $http_host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
  location /socket.io/ {
    proxy_pass http://127.0.0.1:9500;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-Host $http_host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
}
```


## 🔒️ 许可协议
- 本项目在遵循 [**GNU GENERAL PUBLIC LICENSE v3.0**](https://www.gnu.org/licenses/gpl-3.0.html) 许可协议下进行发布
