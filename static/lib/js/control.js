import { changeScheme, showDialog, showProcessingBox, showTextBox, showCodeEditBox,
    convertBashColor, formatTime, formatSize, createTable
} from './utils.js';
import { getLatestVersion, executeCmd, getDetailInfo, getPlayerListInfo, getRoomListInfo,
    startServer, stopServer, updateServer, getServerConfig, backupServer, 
    setServerConfig, modifyServerPort, getServerStatistics, getServerTransTable,
    getPackGitTree, setPackVersion, getBranchCommits
} from './net.js'

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
let trans_table = {};

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
    if(player_list_refresh_btn.hasAttribute('disabled')) {
      return;
    }
    else if(!handled && session_type != 'tmux') {
      showDialog('此服务器不是由本程序接管启动，且非tmux服，无法进此操作');
      return;
    }
    player_list_refresh_btn.style.animation = 'rotate 1s';
    player_list_refresh_btn.setAttribute('disabled', '');
    setTimeout(()=>{player_list_refresh_btn.style.animation = '';}, 1200);
    getPlayerListInfo(server_name, (data)=>{
      if(data?.retcode != 0) {
        showDialog(data?.msg, '提示');
        return;
      }
      let info = data.data;
      refreshPlayerList(info);
      player_list_refresh_btn.removeAttribute('disabled');
    }, base_url_slash);
  });

  // 对房间列表刷新按钮进行点击监听
  let room_list_refresh_btn = document.querySelector('#room_list .list-title .btn');
  room_list_refresh_btn.addEventListener('click', ()=>{
    if(room_list_refresh_btn.hasAttribute('disabled')) {
      return;
    }
    else if(!handled && session_type != 'tmux') {
      showDialog('此服务器不是由本程序接管启动，且非tmux服，无法进此操作');
      return;
    }
    room_list_refresh_btn.style.animation = 'rotate 1s';
    room_list_refresh_btn.setAttribute('disabled', '');
    setTimeout(()=>{room_list_refresh_btn.style.animation = '';}, 1200);
    getRoomListInfo(server_name, (data)=>{
      if(data?.retcode != 0) {
        showDialog(data?.msg, '提示');
        return;
      }
      let info = data.data;
      refreshRoomList(info);
      room_list_refresh_btn.removeAttribute('disabled');
    }, base_url_slash);
  });

  setTimeout(()=>{
    getLatestVersion((data)=>{
      if(data?.retcode != 0) {
        showDialog(data?.msg, '提示');
      }
      document.getElementById('latest_version').innerHTML = data.data.version;
    }, base_url_slash);
  }, 1000);
};

// 刷新服务器详细信息
function refreshDetails(show_error=true) {
  getDetailInfo(server_name, (data)=>{
    if(data?.retcode != 0) {
      if(data?.msg && show_error) {
        showDialog(data?.msg, '提示');
      }
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
    <div class="capsule" title="`+name+`">
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
    <div class="capsule" title="`+name+`">
        <i class="bi">&#xF422;</i>
        <span>`+'['+index+'] '+name+`</span>
    </div>
    `
    list_div.insertAdjacentHTML('BeforeEnd', div);
  }
}

// 刷新拓展包列表
async function refreshPackList(pack_list) {
  let list_div = document.querySelector('#pack_list .list-content');
  list_div.innerHTML = '';
  for(let code in pack_list) {
    let name = pack_list[code].name;
    let url = pack_list[code].url;
    let hash = pack_list[code].hash;
    let enabled = pack_list[code].enabled;
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
    if(!url) {
      badge += '<badge>内置包</badge>';
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
      <div class="capsule">
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
    <div class="capsule pack"`+style+` data-code=`+code+` data-enable=`+enabled+`>
        <details>
          <summary>
            <i class="bi" title="拓展包名">&#xF7D3;</i>
            <span title="`+name+`">`+name+' ('+code+')'+`</span>
            <badge class="disabled">未启用</badge>
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
          <div `+info_style+`>
            <div class="btn package-change-btn">切换拓展包版本</div>
          </div>
          <div style="display:flex;flex-wrap:wrap;">`+packs+`</div>
        </details>
    </div>
    `;
    list_div.insertAdjacentHTML('BeforeEnd', div);

    document.querySelector('.pack[data-code='+code+'] .package-change-btn').onclick = ()=>{
      changePackVersion(code, name, url, hash);
    };
  }
}

// 更改拓展包版本
function changePackVersion(code, name, url, hash) {
  showProcessingBox(
    '获取拓展包“'+name+'”版本信息中...',
    '版本列表',
    (pre, final_callback)=>{
      getPackGitTree(url, (data)=>{
        if(data?.retcode == 0) {
            pre.classList.add('center');
            pre.innerHTML = '<b>'+name+'('+code+')最新一百条提交记录</b>';
            pre.appendChild(createGitList(data?.data, code, name, url, hash));
            final_callback(true);
        } else {
          final_callback(false);
          let msg = data?.msg;
          if(msg) {
            if (msg.toLowerCase().includes('rate limit exceeded')) {
              msg += '<br><br>检测到您的访问已被速率限制，无法正常访问，您也可以在下方输入令牌，以指定身份访问API'
                  +'(获取令牌: [<a href="https://gitee.com/profile/personal_access_tokens" style="text-decoration:underline;">Gitee</a>]'
                  +' [<a href="https://github.com/settings/tokens" style="text-decoration:underline;">GitHub</a>])';
              showTextBox(msg, '速率限制', (token)=>{
                if (token) {
                  localStorage.setItem('gitToken', token);
                }
              });
              return;
            }
            if (msg.toLowerCase().includes('unauthorized') || msg.toLowerCase().includes('bad credentials')) {
              msg += '<br><br>检测到您的API已失效，已自动清除，请重新进行请求';
              localStorage.removeItem('gitToken');
              showDialog(msg);
              return;
            }
            showDialog(msg);
          }
        }
      }, base_url_slash);
    }
  );
}

// 通过拓展包的Git历史生成可以切换的历史版本列表
function createGitList(tree, pack_code, pack_name, pack_url, hash) {

  // 新增提交记录到分支页面
  function addCommitToPage(page, commit) {
    let message = commit.message;
    let author = commit.author;
    let sha = commit.sha;
    let commit_div = document.createElement('div');
    commit_div.classList.add('capsule');
    commit_div.innerHTML = `
      <i class="bi" title="描述">&#xF251;</i>
      <span style="flex-grow:1;">`+message+`</span>
      <i class="bi" title="作者">&#xF4DA;</i>
      <span style="white-space:nowrap;">`+author+`</span>
      <i class="bi" title="版本">&#xF69D;</i>
      <span style="white-space:nowrap;">`+sha.slice(0, 8)+`</span>
    `;
    let toggle_div = document.createElement('div');
    let toggle_btn = document.createElement('div');
    toggle_btn.classList.add('btn');
    toggle_btn.innerText = '切换';
    toggle_btn.dataset.sha = sha;
    toggle_btn.onclick = (e)=>{
      let new_hash = e.target.dataset.sha;
      setPackVersion(
        server_name,
        pack_name,
        pack_code,
        branch,
        hash,
        new_hash,
        base_url_slash)
      ;
    };
    toggle_div.appendChild(toggle_btn);
    commit_div.appendChild(toggle_div);
    page.appendChild(commit_div);
  }

  // 切换分支
  function togglePage(self) {
    let branch = self.target.dataset.name;
    let branch_hash = self.target.dataset.sha;
    let commit_page = document.getElementById(branch);
    document.querySelectorAll('#git_nav li').forEach((e)=>e.classList.remove('active'));
    self.target.classList.add('active');
    document.querySelectorAll('.commit_page').forEach((e)=>e.classList.remove('active'));
    commit_page.classList.add('active');
    if (commit_page.querySelector('.capsule')) {
      return;
    }
    getBranchCommits(pack_url, branch_hash, (data)=>{
      if(data?.retcode == 0) {
        commit_page.innerHTML = '';
        let commits = data.data;
        for(let i in commits) {
          let commit = commits[i];
          addCommitToPage(commit_page, commit);
        }
      } else {
        if(data?.msg) showDialog(data?.msg);
      }
    }, base_url_slash);
  }

  let has_active = false;

  let git_nav = document.createElement('ul');
  git_nav.id = 'git_nav';
  let git_content = document.createElement('div');
  git_content.id = 'git_content';

  for(let branch in tree) {
    let branch_li = document.createElement('li');
    branch_li.innerText = branch;
    branch_li.dataset.name = branch;
    branch_li.dataset.sha = tree[branch].sha;
    branch_li.onclick = togglePage;
    let commit_page = document.createElement('div');
    commit_page.id = branch;
    commit_page.classList.add('commit_page');
    for(let i in tree[branch].commits) {
      let commit = tree[branch].commits[i];
      addCommitToPage(commit_page, commit);
    }
    if (tree[branch].commits.length == 0) {
      commit_page.innerHTML = '<i class="bi rotate"><b>&#xF130;</b></i>';
    }
    git_content.appendChild(commit_page);
    if (!has_active && tree[branch].commits.length != 0) {
      git_nav.insertBefore(branch_li, git_nav.firstChild);
      branch_li.classList.add('active');
      commit_page.classList.add('active');
      has_active = true;
    } else {
      git_nav.appendChild(branch_li);
    }
  }
  let div = document.createElement('div');
  div.id = 'git_tree';
  div.appendChild(git_nav);
  div.appendChild(git_content);
  return div;
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
  cover.style.display = 'flex';
});
socket.on('connect_error', function() {
  cover.style.display = 'flex';
});

// 监控命令输入框的按键，并实现指令历史记录
let terminal_input = document.querySelector('.terminal-input input');
const history = localStorage.getItem('cmd_history') ? JSON.parse(localStorage.getItem('cmd_history')) : [];
let currentIndex = history.length;
terminal_input.addEventListener('keyup', function(e) {
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
          if(data?.retcode != 0) {
            if(data?.msg) showDialog(data?.msg);
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
      if(data?.msg) showDialog(data?.msg);
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
      if(data?.msg) showDialog(data?.msg);
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
          if(data?.retcode == 0 || data?.code == 405) {
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
            if(data?.msg) showDialog(data?.msg);
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
    updateServer(server_name, ()=>{
      refreshDetails(false);
    }, base_url_slash);
  } else {
    showDialog('服务器已经是最新版本，是否强制更新？', '提示', ()=>{
      updateServer(server_name, ()=>{
        refreshDetails(false);
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
            if(data?.msg) showDialog(data?.msg);
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
    '统计信息',
    (pre, final_callback)=>{
      getServerTransTable(server_name, (data)=>{
        if(data?.retcode == 0) {
          trans_table = data?.data;
        }
        getServerStatistics(server_name, (data)=>{
          if(data?.retcode == 0) {
            pre.classList.add('center');
            pre.style.padding = '1rem';
            pre.innerHTML = '<b>今日活跃人数：' + data?.data.daily_active + '</b><br>';
            pre.innerHTML += '<b>本月活跃人数：' + data?.data.month_active + '</b>';
            let hr = document.createElement("hr");
            hr.style.width = '90%';
            pre.appendChild(hr);
            let player_win_rate = data?.data.player_win_rate;
            let general_win_rate = data?.data.general_win_rate;
            for(let mode in player_win_rate) {
              let mode_title = mode;
              if (mode == '0_all') {
                mode_title = '全部模式';
                if(Object.keys(player_win_rate[mode]).length == 0) {
                  pre.innerHTML += '<span>玩家胜率表为空</span>';
                  continue;
                }
              }else if (mode in trans_table) {
                mode_title = trans_table[mode];
              }
              pre.appendChild(createTable(
                '▶玩家胜率表<'+mode_title+'>',
                ['玩家名', '胜率', '胜场', '输场', '平局', '总计'],
                player_win_rate[mode],
                trans_table,
                false
              ));
            }
            hr = document.createElement("hr");
            hr.style.width = '90%';
            pre.appendChild(hr);
            for(let mode in general_win_rate) {
              let mode_title = mode;
              if (mode == '0_all') {
                mode_title = '全部模式';
                if(Object.keys(general_win_rate[mode]).length == 0) {
                  pre.innerHTML += '<span>角色胜率表为空</span>';
                  continue;
                }
              }else if (mode in trans_table) {
                mode_title = trans_table[mode];
              }
              pre.style.padding = '1rem';
              pre.appendChild(createTable(
                '▶角色胜率表<'+mode_title+'>',
                ['角色名', '胜率', '胜场', '输场', '平局', '总计'],
                general_win_rate[mode],
                trans_table,
                false
              ));
            }
            final_callback(true);
          } else {
            final_callback(false);
            if(data?.msg) showDialog(data?.msg);
          }
        }, base_url_slash);
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
        if(data?.msg) showDialog(data?.msg);
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
                if(data?.msg) showDialog(data?.msg);
              }, base_url_slash)
            }
          );
        } else {
          final_callback(false);
          if(data?.msg) showDialog(data?.msg);
        }
      }, base_url_slash);
    }
  );
});
