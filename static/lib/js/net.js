import { showDialog, showProcessingBox } from './utils.js';

// GET Method
async function get(url, callback) {
  fetch(url, {
    method:'GET'
  }).then(res => {
    const contentType = res.headers.get('content-type');
    if(contentType == 'application/json') {
      return res.json();
    } else {
      res.text().then(text => {
        showDialog(text);
        return null;
      });
    }
  }).then(data => callback(data))
    .catch(error => {
      showDialog(error, '请求出错');
      callback();
  });
}

// POST Method
async function post(url, data, callback) {
  fetch(url, {
    method:'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  }).then(res => {
    const contentType = res.headers.get('content-type');
    if(contentType == 'application/json') {
      return res.json();
    } else {
      res.text().then(text => {
        showDialog(text);
        return null;
      });
    }
  }).then(data => callback(data))
    .catch(error => {
      showDialog(error, '请求出错');
      callback();
  });
}

// 获取服务器列表
export function getServerList(callback, base_url='') {
  get(base_url + 'v1/servers', callback);
}

// 启动服务器
export function startServer(name, callback, base_url='') {
  let data = {'name': name};
  post(base_url + 'v1/start_server', data, callback);
}

// 停止服务器
export function stopServer(name, callback, base_url='') {
  let data = {'name': name};
  post(base_url + 'v1/stop_server', data, callback);
}

// 删除服务器
export function deleteServer(name, callback, base_url='') {
  let data = {'name': name};
  post(base_url + 'v1/del_server', data, callback);
}

// 更新服务器
export function updateServer(name, callback, base_url='') {
  showDialog(
    `
    你真的要更新服务器<`+name+`>吗？<br>您的服务器将会执行如下指令
    <details>
      <summary>更新指令</summary>
      <p>git reset --hard</p>
      <p>git pull --tags origin master</p>
      <p>latest_tag=$(git describe --tags \`git rev-list --tags --max-count=1\`)</p>
      <p>git checkout $latest_tag</p>
      <p>[ -f include/lua.h ] || cp -r /usr/include/lua5.4/* include</p>
      <p>[ -d build ] || mkdir build</p>
      <p>cd build</p>
      <p>cmake .. -DFK_SERVER_ONLY=</p>
      <p>make</p>
      <p>cd ..</p>
      <p>[ -f FreeKill ] || ln -s build/FreeKill</p>
    </details>
    `,
    '警告',
    ()=>{
      showProcessingBox(
        '更新服务器中...',
        '提示',
        (pre, final_callback)=>{
          let eventSource = new EventSource(base_url + 'v1/update_server?name='+name);
          eventSource.onmessage = (event)=>{
            pre.innerHTML += '\n'+event.data;
            pre.scrollTop = pre.scrollHeight - pre.clientHeight;
          };
          eventSource.onerror = ()=>{
              eventSource.close();
              final_callback(true);
              callback();
          };
        }
      );
    }
  );
}

// 获取FreeKill最新版本
export function getLatestVersion(callback, base_url='') {
  get(base_url + 'v1/check_version?type=FreeKill', callback);
}

// 执行终端指令
export function executeCmd(name, cmd, callback, base_url='') {
  let data = {'name': name, 'cmd': cmd};
  post(base_url + 'v1/execute', data, callback);
}

// 获取服务器详细信息
export function getDetailInfo(name, callback, base_url='') {
  get(base_url + 'v1/details?name='+name, callback);
}

// 获取服务器玩家列表
export function getPlayerListInfo(name, callback, base_url='') {
  get(base_url + 'v1/player_list?name='+name, callback);
}

// 获取服务器房间列表
export function getRoomListInfo(name, callback, base_url='') {
  get(base_url + 'v1/room_list?name='+name, callback);
}

// 获取服务器配置文件
export function getServerConfig(name, callback, base_url='') {
  get(base_url + 'v1/config?name='+name, callback);
}

// 设置服务器配置文件
export function setServerConfig(name, config, callback, base_url='') {
  let data = {'name': name, 'config': config};
  post(base_url + 'v1/config', data, callback);
}

// 修改服务器端口
export function modifyServerPort(name, port, callback, base_url='') {
  let data = {'name': name, 'port': port};
  post(base_url + 'v1/modify', data, callback);
}

// 对服务器进行备份
export function backupServer(name, callback, base_url='') {
  let data = {'name': name};
  post(base_url + 'v1/backup', data, callback);
}

// 获取服务器统计数据
export function getServerStatistics(name, callback, base_url='') {
  get(base_url + 'v1/statistics?name='+name, callback);
}
