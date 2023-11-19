import { setScheme, showDialog, convertBashColor, addSecondsToTime } from './utils.js';

// 主题相关
const themeScheme = window.matchMedia('(prefers-color-scheme: light)');
document.getElementById('color_scheme').addEventListener('click', changeScheme);
themeScheme.addEventListener('change', (e)=>{
  if (themeScheme.matches) {
    setScheme('light');
  } else {
    setScheme('dark');
  }
});
const evt = new Event('change', { bubbles: true, cancelable: true });
themeScheme.dispatchEvent(evt);

function changeScheme(){
  if (getComputedStyle(document.querySelector('html')).colorScheme == 'light') {
    setScheme('dark');
  } else {
    setScheme('light');
  }
}

// 页面加载完毕后触发
window.onload = function() {
  setInterval(() => {
    document.querySelectorAll('#server_time').forEach((e)=>{
      let origin_time = e.innerText;
      if(origin_time != '0') {
        let calc_time = addSecondsToTime(origin_time, 1);
        e.innerText = calc_time;
      }
    });
  }, 1000);

  document.querySelector('#refresh_btn').addEventListener('click', ()=>{
    location.reload();
  });
};


// 获取当前服务器名URL
let name = decodeURIComponent(window.location.pathname.split('/').pop());
let base_url = window.location.pathname.replace('/control/', '/');
base_url = base_url.substring(0, base_url.lastIndexOf('/'));

document.querySelector('#title a').innerText = name;

// 实时监控终端
let screen = document.querySelector('.terminal-screen');
let cover = document.querySelector('.terminal-cover');
let socket = io.connect(base_url, {
  query: "name="+name
});
socket.on('log', function(data) {
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
  screen.scrollTop = screen.scrollHeight - screen.clientHeight;
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
let currentIndex = 0;
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
    if (currentValue !== '') {
      if(history.length >= 50) {
        history.shift();
      }
      history.push(currentValue);
      localStorage.setItem('cmd_history', JSON.stringify(history));
      currentIndex = history.length;
      execute(terminal_input.value, ()=>{
        terminal_input.value = '';
      });
    }
    terminal_input.value = history[currentIndex] || '';
  }
});

// 执行终端指令
function execute(cmd, callback) {
  let data = {'name': name, 'cmd': cmd};
  fetch(base_url + '/v1/execute',{
    method:'POST',
    headers: {
    'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
  }).then(res => res.json())
    .then(data => {
      if(data.retcode != 0) {
        showDialog(data.msg, '提示');
      }
      callback();
    })
    .catch(error => {
      showDialog(error, '请求出错');
  })
}

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

// 获取服务器详细信息
function getDetailInfo(callback) {
  let data = {'name': name};
  fetch(base_url + '/v1/details',{
    method:'POST',
    headers: {
    'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
  }).then(res => res.json())
    .then(data => {
      if(data.retcode != 0) {
        showDialog(data.msg, '提示');
      }
      callback(data.data);
    })
    .catch(error => {
      showDialog(error, '请求出错');
  })
}
getDetailInfo((info)=>{
  console.log(info);
  if(info.icon) {
    document.querySelectorAll('#server_icon').forEach((e)=>{
      e.src = info.icon;
      e.style.display = 'inline-block';
    });
  }
  document.getElementById('server_name').innerHTML = info.name;
  document.getElementById('server_version').innerHTML = info.version;
  document.getElementById('server_desc').innerHTML = info.desc;
  document.getElementById('server_motd').innerHTML = info.motd;
  document.getElementById('server_port').innerHTML = info.port;
  document.getElementById('server_pid').innerHTML = info.pid;
  document.getElementById('server_enable_bots').innerHTML = info.enable_bots?'启用':'禁用';
  document.getElementById('server_temp_ban_time').innerHTML = info.temp_ban_time + '分钟';
  document.getElementById('server_time').innerHTML = info.runtime;
});


// 获取FreeKill最新版本
function getLatestVersion(callback) {
  fetch(base_url + '/v1/check_version?type=FreeKill',{
    method:'GET'
  }).then(res => res.json())
    .then(data => {
      if(data.retcode != 0) {
        showDialog(data.msg, '提示');
      }
      callback(data.data.version);
    })
    .catch(error => {
      showDialog(error, '请求出错');
  })
}
getLatestVersion((version)=>{
  document.getElementById('latest_version').innerHTML = version;
});
