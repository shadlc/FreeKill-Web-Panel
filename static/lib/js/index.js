import { setScheme, showDialog } from './utils.js'

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

};

// 获取服务器列表
function refresh_servers() {
  let refresh_btn = document.querySelector('#refresh_btn>span');
  refresh_btn.style.animation = 'rotate 1s';

  fetch('v1/servers', {
    method:'GET'
  }).then(res => {
    setTimeout(()=>{refresh_btn.style.animation = '';}, 1200);
    return res.json();
  }).then(data => render_server_list(data.data.list))
    .catch(error => {
      showDialog(error, '请求出错');
  });
}
document.querySelector('#refresh_btn').addEventListener('click', refresh_servers);
refresh_servers();

// 绘制服务器列表
function render_server_list(servers){
  document.querySelectorAll('.server-item').forEach((e)=>{
    e.remove();
  })

  let list_div = document.getElementById('server_list');
  for(let i in servers){
    let info = servers[i];
    let server_div = `
    <div id="server`+info.pid+`" class="server-item">
        <img class="server-icon" src="`+info.icon+`" />
        <div class="server-info">
            <a class="server-link" href="control/`+info.pid+`">
                <h2 class="server-name">`+info.name+`</h2>
                <p1 class="server-desc">`+info.desc+`</p1>
                <span class="server-pid">`+info.pid+`</span>
            </a>
            <div class="capsule-box">
                <i class="bi server-status">&#xF4FF;</i>
                <span class="server-status">`+info.status+`</span>
                <i class="bi server-port">&#xF6D5;</i>
                <span class="server-port">`+info.port+`</span>
                <i class="bi server-players">&#xF4CF;</i>
                <span class="server-players">`+info.players+'/'+info.capacity+`</span>
                <i class="bi server-version">&#xF69D;</i>
                <span class="server-version">`+info.version+`</span>
                <i class="bi server-time">&#xF293;</i>
                <span class="server-time">`+info.runtime+`</span>
            </div>
        </div>
        <div class="server-toggle">
            <i class="bi">&#xF5D3;</i>
        </div>
    </div>`
    list_div.insertAdjacentHTML('BeforeEnd', server_div);
  }
  if(list_div.innerHTML == '') {
    const empty_div = `<span id="empty_text">服务器列表为空，请点击左上角</span>`
    list_div.insertAdjacentHTML('BeforeEnd', empty_div);
  }
  initServerToggleBtn();
}

// 初始化服务器配置按钮
function initServerToggleBtn() {
  function handleMenuClick(event) {
    document.querySelectorAll('.server-menu').forEach((e)=>{e.remove()});
    let div_id = event.target.parentNode.parentNode.id;
    let server_name = document.querySelector('#'+div_id+' .server-name').innerText;
    let server_pid = document.querySelector('#'+div_id+' .server-pid').innerText;
    let menu = document.createElement('div');
    menu.classList.add('server-menu');
    menu.innerHTML = `
      <span><i class="bi">&#xF3E2; </i>详情</span>
      <span><i class="bi">&#xF4F4; </i>启动</span>
      <span><i class="bi">&#xF592; </i>停止</span>
      <span><i class="bi">&#xF5DD; </i>删除</span>
    `;
    document.body.appendChild(menu);

    let mouseX = event.clientX;
    let mouseY = event.clientY;
    let menuWidth = menu.offsetWidth;
    let menuHeight = menu.offsetHeight;
    let windowWidth = window.innerWidth;
    let windowHeight = window.innerHeight;

    let top, left;
    if (mouseX + menuWidth > windowWidth) {
      left = mouseX - menuWidth;
    } else {
      left = mouseX;
    }
    if (mouseY + menuHeight > windowHeight) {
      top = mouseY - menuHeight;
    } else {
      top = mouseY;
    }
    menu.style.top = top + 'px';
    menu.style.left = left + 'px';

    menu.querySelectorAll('span').forEach(function(span) {
      span.addEventListener('click', ()=>{
        if(span.innerText.includes('详情')) {
          window.open('control/'+server_pid);
        } else if(span.innerText.includes('启动')) {
          start_server(server_name, server_pid);
        } else if(span.innerText.includes('停止')) {
          showDialog('你真的要停止服务器<'+server_name+'>吗？', '警告',
          ()=>{stop_server(server_name, server_pid);})
        } else if(span.innerText.includes('删除')) {
          showDialog('你真的要停止并删除服务器<'+server_name+'>吗？', '警告',
          ()=>{delete_server(server_name, server_pid);})
        }
      });
    });
    function handleDocumentClick(event) {
      if (!event.target.parentNode.classList.contains('server-toggle')) {
        document.removeEventListener('click', handleDocumentClick);
        menu.remove();
      }
    }
    document.addEventListener('click', handleDocumentClick);
  }
  let divs = document.querySelectorAll('.server-toggle');
  divs.forEach(function(div) {
    div.addEventListener('click', handleMenuClick);
  });
}

// 添加服务器
document.getElementById("start_server_btn").addEventListener("click", ()=>{
  let btn = document.getElementById("start_server_btn");
  btn.disabled = true;
  add_server(()=>{btn.disabled = false;});
});
function add_server(callback) {
  let name = document.getElementById('server_name_input').value
  let port = document.getElementById('server_port_input').value
  let path = document.getElementById('server_path_input').value
  let desc = document.getElementById('server_desc_input').value
  let icon_url = document.getElementById('icon_url_input').value
  let capacity = document.getElementById('capacity_input').value
  let temp_ban_time = document.getElementById('temp_ban_time_input').value
  let motd = document.getElementById('motd_input').value
  let enable_bots = document.getElementById('enable_bots_input').value
  let data = {"name": name,
              "port": port,
              "path": path,
              "desc": desc,
              "icon": icon_url,
              "capacity": capacity,
              "temp_ban_time": temp_ban_time,
              "motd": motd,
              "enable_bots": enable_bots,
            }
  fetch('v1/add_server', {
    method:'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
  }).then(res => res.json())
    .then(data => {
      showDialog(data. msg, '提示', ()=>{
        if(data.retcode == 0) {
          refresh_servers();
          document.getElementById('add_modal').style.display = 'none';
        }
      });
    })
    .catch(error => {
      showDialog(error, '请求出错');
  }).then(callback())
}

// 启动服务器
function start_server(name, pid) {
  fetch('v1/start_server?name='+name, {
    method:'GET'
  }).then(res => res.json())
    .then(data => {
      if(data.retcode == 0) {
        document.querySelector('#server'+pid).remove();
      }
      refresh_servers();
      showDialog(data.msg);
    })
    .catch(error => {
      showDialog(error, '请求出错');
  });
}

// 停止服务器
function stop_server(name) {
  fetch('v1/stop_server?name='+name, {
    method:'GET'
  }).then(res => res.json())
    .then(data => {
      refresh_servers();
      showDialog(data.msg);
    })
    .catch(error => {
      showDialog(error, '请求出错');
  });
}

// 删除服务器
function delete_server(name, pid) {
  fetch('v1/del_server?name='+name, {
    method:'GET'
  }).then(res => res.json())
    .then(data => {
      if(data.retcode == 0) {
        document.querySelector('#server'+pid).remove();
      }
      refresh_servers();
      showDialog(data.msg);
    })
    .catch(error => {
      showDialog(error, '请求出错');
  });
}