import { changeScheme, showDialog, showProcessingBox, showTextBox, showCodeEditBox, convertBashColor, formatTime, formatSize } from './utils.js';
import { getLatestVersion, executeCmd, getDetailInfo, startServer, stopServer, updateServer, getServerConfig, setServerConfig, modifyServerPort, getPlayerListInfo, getRoomListInfo, backupServer, getServerStatistics } from './net.js'

// 主题相关
const themeScheme = window.matchMedia('(prefers-color-scheme: light)');
themeScheme.addEventListener('change', (e)=>{
  if (themeScheme.matches) {
    changeScheme('light');
  } else {
    changeScheme('dark');
  }
});
document.getElementById('color_scheme').addEventListener('click', changeScheme);
const evt = new Event('change', { bubbles: true, cancelable: true });
themeScheme.dispatchEvent(evt);

// 获取当前服务器名URL
let server_name = decodeURIComponent(window.location.pathname.split('/').pop());
let base_url = window.location.href.replace('/control/', '/');
base_url = base_url.substring(0, base_url.lastIndexOf('/'));
let base_url_slash = base_url + '/';

document.querySelector('#title').innerText = server_name;

let start_time = 0;
let handled = false;
let session_type = '';

// 页面加载完毕后触发
window.onload = function() {
  refreshDetails();

  setInterval(() => {
    refreshTime();
  }, 1000);

  document.querySelector('#refresh_btn').addEventListener('click', ()=>{
    location.reload();
  });

  document.querySelector('#server_motd').addEventListener('click', ()=>{
    showDialog(document.querySelector('#server_motd')?.innerHTML, '公告', undefined, true);
  });

  // 对玩家列表刷新按钮进行点击监听
  let player_list_refresh_btn = document.querySelector('#player_list .list-title .btn');
  player_list_refresh_btn.addEventListener('click', ()=>{
    if(player_list_refresh_btn.style.cursor == 'not-allowed') {
      return;
    }
    else if(!handled && session_type != 'tmux') {
      showDialog('此服务器不是由本程序接管启动，且非tmux服，无法进此操作');
      return;
    }
    player_list_refresh_btn.style.animation = 'rotate 1s';
    player_list_refresh_btn.style.enabled = false;
    player_list_refresh_btn.style.cursor = 'not-allowed';
    setTimeout(()=>{player_list_refresh_btn.style.animation = '';}, 1200);
    getPlayerListInfo(server_name, (data)=>{
      if(data.retcode != 0) {
        showDialog(data?.msg, '提示');
        return;
      }
      let info = data.data;
      refreshPlayerList(info);
      player_list_refresh_btn.style.cursor = '';
    }, base_url_slash);
  });

  // 对房间列表刷新按钮进行点击监听
  let room_list_refresh_btn = document.querySelector('#room_list .list-title .btn');
  room_list_refresh_btn.addEventListener('click', ()=>{
    if(room_list_refresh_btn.style.cursor == 'not-allowed') {
      return;
    }
    else if(!handled && session_type != 'tmux') {
      showDialog('此服务器不是由本程序接管启动，且非tmux服，无法进此操作');
      return;
    }
    room_list_refresh_btn.style.animation = 'rotate 1s';
    room_list_refresh_btn.style.enabled = false;
    room_list_refresh_btn.style.cursor = 'not-allowed';
    setTimeout(()=>{room_list_refresh_btn.style.animation = '';}, 1200);
    getRoomListInfo(server_name, (data)=>{
      if(data.retcode != 0) {
        showDialog(data?.msg, '提示');
        return;
      }
      let info = data.data;
      refreshRoomList(info);
      room_list_refresh_btn.style.cursor = '';
    }, base_url_slash);
  });

  setTimeout(()=>{
    getLatestVersion((data)=>{
      if(data.retcode != 0) {
        showDialog(data?.msg, '提示');
      }
      document.getElementById('latest_version').innerHTML = data.data.version;
    }, base_url_slash);
  }, 1000);
};

// 刷新服务器详细信息
function refreshDetails() {
  getDetailInfo(server_name, (data)=>{
    if(data.retcode != 0) {
      showDialog(data?.msg, '提示');
      return;
    }
    let info = data.data;
    if(info.icon) {
      document.querySelectorAll('#server_icon').forEach((e)=>{
        e.src = info.icon;
        e.style.display = 'inline-block';
      });
    }
    handled = info.handled;
    session_type = info.session_type;
    document.getElementById('server_name').innerHTML = info.name;
    document.getElementById('server_version').innerHTML = info.version;
    document.getElementById('server_desc').innerHTML = info.desc;
    document.getElementById('server_motd').innerHTML = info.motd;
    document.getElementById('server_port').innerHTML = info.port;
    document.getElementById('server_pid').innerHTML = info.pid;
    document.getElementById('server_enable_bots').innerHTML = info.enable_bots?'启用':'禁用';
    document.getElementById('server_temp_ban_time').innerHTML = info.temp_ban_time + '分钟';
    refreshPackList(info.pack_list);
    if(info.uptime != 0) {
      start_time = Date.now() - info.uptime * 1000;
    } else {
      start_time = 0;
    }
    refreshTime(info.status);
  }, base_url_slash);
}

// 刷新服务器运行时长
function refreshTime(status) {
  if(start_time == 0) {
    if(status) document.getElementById('server_time').innerHTML = status;
  } else {
    let uptime = Date.now() - start_time;
    let string_time = formatTime(uptime);
    document.getElementById('server_time').innerHTML = string_time;
  }
}

// 刷新玩家列表
async function refreshPlayerList(player_list) {
  let list_div = document.querySelector('#player_list .list-content');
  list_div.innerHTML = '';
  for(let index in player_list) {
    let name = player_list[index]
    let div = `
    <div class="capsule-box" title="`+name+`">
        <i class="bi">&#xF4DA;</i>
        <span>`+'['+index+'] '+name+`</span>
    </div>
    `
    list_div.insertAdjacentHTML('BeforeEnd', div);
  }
}

// 刷新房间列表
async function refreshRoomList(room_list) {
  let list_div = document.querySelector('#room_list .list-content');
  list_div.innerHTML = '';
  for(let index in room_list) {
    let name = room_list[index]
    let div = `
    <div class="capsule-box" title="`+name+`">
        <i class="bi">&#xF422;</i>
        <span>`+'['+index+'] '+name+`</span>
    </div>
    `
    list_div.insertAdjacentHTML('BeforeEnd', div);
  }
}

// 刷新扩充包列表
async function refreshPackList(pack_list) {
  let list_div = document.querySelector('#pack_list .list-content');
  list_div.innerHTML = '';
  for(let code in pack_list) {
    let name = pack_list[code].name;
    let url = pack_list[code].url;
    let hash = pack_list[code].hash;
    let pack_count = 0;
    if(pack_list[code]?.packs) {
      pack_count = Object.keys(pack_list[code].packs).length;
    }
    let badge = '';
    let style = '';
    let info_style = '';
    if(pack_count) {
      badge += '<badge>'+pack_count+'子包</badge>';
    } else {
      badge += '<badge>无子包</badge>';
    }
    if(pack_list[code].enabled === 0) {
      style = ' style="opacity:0.6;"'
      badge += '<badge>未启用</badge>'
    }
    if(url) {
      badge += '<badge>可更新包</badge>';
    } else {
      info_style = ' style="display:none;"';
    }

    let packs = ''
    for(let pack in pack_list[code].packs) {
      let pack_info = pack_list[code].packs[pack]
      let pack_type = '角色包';
      if(pack_info.type == 'card') {
        pack_type = '卡牌包';
      } else if(pack_info.type == 'mode') {
        pack_type = '模式包';
      }
      packs += `
      <div class="capsule-box">
        <i class="bi" title="子包名称">&#xF5AF;</i>
        <span title="`+pack_info.name+`">`+pack_info.name+`</span>
        <i class="bi" title="子包代码">&#xF351;</i>
        <span title="`+pack+`">`+pack+`</span>
        <i class="bi" title="子包类型">&#xF2C9;</i>
        <span title="`+pack_type+`">`+pack_type+`</span>
      </div>
      `;
    }

    let div = `
    <div class="capsule-box"`+style+`>
        <details>
          <summary>
            <i class="bi" title="扩展包名">&#xF7D3;</i>
            <span title="`+name+`">`+name+' ('+code+')'+`</span>
            `+badge+`
          </summary>
          <div `+info_style+`>
            <i class="bi" title="更新地址">&#xF69D;</i>
            <span title="更新地址">地址</span>
            <span title="`+url+`">`+url+`</span>
          </div>
          <div `+info_style+`>
            <i class="bi" title="版本">&#xF40A;</i>
            <span title="版本">版本</span>
            <span title="`+hash+`">`+hash+`</span>
          </div>
          <div style="display:flex;flex-wrap:wrap;">`+packs+`</div>
        </details>
    </div>
    `;
    list_div.insertAdjacentHTML('BeforeEnd', div);
  }
}

// 实时监控终端
let screen = document.querySelector('.terminal-screen');
let cover = document.querySelector('.terminal-cover');
let socket = io.connect(base_url+'?name='+server_name);
// 实时获取游戏终端输出
socket.on('terminal', function(data) {
  cover.style.display = 'none';
  if(data.history) {
    let text = convertBashColor(data.text);
    while(text.match(/[^\x08]\x08/)) {
      text = text.replace(/[^\x08]\x08/, '');
    }
    screen.innerHTML = text;
  }else if(data.text.includes('\x08')) {
    if(data.text == '\x08') {
      screen.innerHTML = screen.innerHTML.slice(0, -1);
    } else {
      let text = screen.innerHTML + data.text;
      while(text.match(/[^\x08]\x08/)) {
        text = text.replace(/[^\x08]\x08/, '');
      }
      screen.innerHTML = text;
    }
  } else {
    screen.innerHTML += convertBashColor(data.text);
  }
  if(data.start && session_type != 'screen') {
    setTimeout(() => {
      refreshDetails();
    }, 1000);
  }
  screen.scrollTop = screen.scrollHeight - screen.clientHeight;
});
// 实时获取服务器CPU与内存占用
socket.on('perf', function(data) {
  if(data.data) {
    document.getElementById('server_cpu').innerHTML = data.data.cpu;
    document.getElementById('server_ram').innerHTML
      = /^\d+$/.test(data.data.ram)?formatSize(data.data.ram):data.data.ram;
  }
});
socket.on('disconnect', () => {
  cover.style.display = 'inherit';
});
socket.on('connect_error', function() {
  cover.style.display = 'inherit';
});

// 监控命令输入框的按键，并实现指令历史记录
let terminal_input = document.querySelector('.terminal-input input');
const history = localStorage.getItem('cmd_history') ? JSON.parse(localStorage.getItem('cmd_history')) : [];
let currentIndex = history.length;
terminal_input.addEventListener('keydown', function(e) {
  if (e.key === 'ArrowUp') {
    e.preventDefault();
    if (currentIndex > 0) {
      currentIndex--;
    }
    terminal_input.value = history[currentIndex] || '';
  } else if (e.key === 'ArrowDown') {
    e.preventDefault();
    if (currentIndex < history.length) {
      currentIndex++;
    }
    terminal_input.value = history[currentIndex] || '';
  } else if (e.key === 'Enter') {
    const currentValue = terminal_input.value.trim();
    if(currentValue == 'start' && session_type == 'screen' && document.getElementById('server_time').innerHTML == '已停止') {
      showDialog('screen服务器暂不支持指令启动');
      return;
    }
    if (currentValue !== '') {
      if(history.length >= 100) {
        history.shift();
      }
      history.push(currentValue);
      localStorage.setItem('cmd_history', JSON.stringify(history));
      currentIndex = history.length;
      executeCmd(
        server_name,
        terminal_input.value,
        (data)=>{
          if(data.retcode != 0) {
            showDialog(data?.msg);
          }
          terminal_input.value = '';
        }, base_url_slash
      );
    }
    terminal_input.value = '';
  }
});

// 展开与收起终端
let terminal = document.querySelector('.terminal');
document.querySelectorAll('.terminal-btn').forEach((e)=>{
  e.addEventListener('click', ()=>{
    if(e.innerText == '▲') {
      e.innerText = '▼'
      terminal.classList.add('terminal-small');
    } else {
      e.innerText = '▲'
      terminal.classList.remove('terminal-small');
    }
  });
})

// 启动服务器按钮
document.getElementById('start_btn').addEventListener('click', ()=>{
  startServer(server_name, (data)=>{
    if(data?.data?.redirect) {
      showDialog('服务器启动成功，由于本服务器是screen启动，服务器名称已发生变动，将在三秒后跳转至新页面');
      setTimeout(() => {
        window.location.href = base_url_slash + 'control/' + data.data.name;
      }, 3000);
    } else {
      showDialog(data?.msg);
      refreshDetails();
    }
  }, base_url_slash);
});

// 停止服务器按钮
document.getElementById('stop_btn').addEventListener('click', ()=>{
  let msg = '你真的要停止服务器<'+server_name+'>吗？'
  if(!handled) {
    msg += '由于本服务器非本程序接管启动，此操作会关闭整个session，是否继续？'
  }
  showDialog(msg, '警告',
  ()=>{
    stopServer(server_name, (data)=>{
      if(data?.retcode == 0 && !handled) {
        showDialog('此服务器不是由本程序接管启动，因此停止后已无法操作，点击确认返回主页，请手动刷新', '提示', ()=>{
          window.location.href = base_url_slash;
        });
      }
      showDialog(data?.msg);
      refreshDetails();
    }, base_url_slash);
  });
});

// 重启服务器按钮
document.getElementById('restart_btn').addEventListener('click', ()=>{
  if(!handled) {
    showDialog('非本程序接管启动的服务器无法使用此功能');
    return;
  }
  showDialog('你真的要重启服务器<'+server_name+'>吗？', '警告',
  ()=>{
    showProcessingBox(
      '重启服务器中...',
      '提示',
      (pre, final_callback)=>{
        stopServer(server_name, (data)=>{
          if(data?.retcode == 0 || data.code == 405) {
            pre.innerHTML += '\n' + data?.msg;
            startServer(server_name, (data)=>{
              if(data?.retcode == 0) {
                pre.innerHTML += '\n服务器重启成功';
                if(data?.data?.redirect) {
                  showDialog('服务器启动成功\n由于本服务器是screen启动，服务器名称已发生变动\n将在三秒后跳转至新页面');
                  setTimeout(() => {
                    window.location.href = base_url_slash + 'control/' + data.data.name;
                  }, 3000);
                  return;
                }
              } else {
                pre.innerHTML += '\n服务器重启失败';
              }
              final_callback(true);
              refreshDetails();
            }, base_url_slash);
          } else {
            final_callback(false);
            showDialog(data?.msg);
          }
        }, base_url_slash);
      }
    );
  })
});

// 更新服务器按钮
document.getElementById('update_btn').addEventListener('click', ()=>{
  const server_version = document.getElementById('server_version').innerHTML;
  const latest_version = document.getElementById('latest_version').innerHTML;
  if(server_version != latest_version) {
    updateServer(server_name, base_url_slash);
  } else {
    showDialog('服务器已经是最新版本，是否强制更新？', '提示', ()=>{
      updateServer(server_name, ()=>{
        refreshDetails();
      }, base_url_slash);
    });
  }
});

// 备份服务器按钮
document.getElementById('backup_btn').addEventListener('click', ()=>{
  showDialog('你真的要对服务器<'+server_name+'>进行备份吗？', '警告',
  ()=>{
    showProcessingBox(
      '备份服务器中...',
      '提示',
      (pre, final_callback)=>{
        backupServer(server_name, (data)=>{
          if(data?.retcode == 0) {
            pre.innerHTML += '\n' + data?.msg;
            final_callback(true);
          } else {
            final_callback(false);
            showDialog(data?.msg);
          }
        }, base_url_slash);
      }
    );
  });
});

// 获取服务器统计信息按钮
document.getElementById('statistics_btn').addEventListener('click', ()=>{
  showProcessingBox(
    '获取数据中...',
    '提示',
    (pre, final_callback)=>{
      getServerStatistics(server_name, (data)=>{
        if(data?.retcode == 0) {
          pre.innerHTML = data?.msg;
          final_callback(true);
        } else {
          final_callback(false);
          showDialog(data?.msg);
        }
      }, base_url_slash);
    }
  );
});

// 修改服务器端口按钮
document.getElementById('port_config_btn').addEventListener('click', ()=>{
  showTextBox(
    '请输入新端口号',
    '端口修改',
    (port)=>{
      modifyServerPort(server_name, port, (data)=>{
        showDialog(data?.msg);
        refreshDetails();
      }, base_url_slash)
    }
  );
});

// 修改服务器配置按钮
document.getElementById('config_btn').addEventListener('click', ()=>{
  showProcessingBox(
    '获取配置文件中...',
    '提示',
    (pre, final_callback)=>{
      getServerConfig(server_name, (data)=>{
        if(data?.retcode == 0) {
          final_callback(false);
          showCodeEditBox(
            '请在下方方框中修改新月杀配置并保存',
            '改操作不可撤销，请注意备份配置文件',
            '配置修改',
            data.data.config,
            (config)=>{
              setServerConfig(server_name, config, (data)=>{
                showDialog(data?.msg);
              }, base_url_slash)
            }
          );
        } else {
          final_callback(false);
          showDialog(data?.msg);
        }
      }, base_url_slash);
    }
  );
});
