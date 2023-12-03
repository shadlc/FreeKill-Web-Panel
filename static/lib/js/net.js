import { showDialog } from './utils.js';

// GET Method
function get(url, callback) {
  fetch(url, {
    method:'GET'
  }).then(res => {
    const contentType = res.headers.get('content-type');
    if(contentType == 'application/json') {
      return res.json()
    } else {
      res.text().then(text => {
        showDialog(text)
      });
    }
  }).then(data => callback(data))
    .catch(error => showDialog(error, '请求出错'));
}

// POST Method
function post(url, data, callback) {
  fetch(url, {
    method:'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  }).then(res => {
    const contentType = res.headers.get('content-type');
    if(contentType == 'application/json') {
      return res.json()
    } else {
      res.text().then(text => {
        showDialog(text)
      });
    }
  }).then(data => callback(data))
    .catch(error => showDialog(error, '请求出错'));
}

// 获取服务器列表
export function getServerList(callback, base_url='') {
  get(base_url + 'v1/servers', callback);
}

// 启动服务器
export function startServer(name, callback, base_url='') {
  get(base_url + 'v1/start_server?name='+name, callback);
}

// 停止服务器
export function stopServer(name, callback, base_url='') {
  get(base_url + 'v1/stop_server?name='+name, callback);
}

// 删除服务器
export function deleteServer(name, callback, base_url='') {
  get(base_url + 'v1/del_server?name='+name, callback);
}

// 获取FreeKill最新版本
export function getLatestVersion(callback, base_url='') {
  get(base_url + '/v1/check_version?type=FreeKill', callback);
}

// 执行终端指令
export function executeCmd(name, cmd, callback, base_url='') {
  let data = {'name': name, 'cmd': cmd};
  post(base_url + '/v1/execute', data, callback);
}

// 获取服务器详细信息
export function getDetailInfo(name, callback, base_url='') {
  let data = {'name': name};
  post(base_url + '/v1/details', data, callback);
}

// 获取服务器配置文件
export function getServerConfig(name, callback, base_url='') {
  get(base_url + '/v1/config?name='+name, callback);
}

// 设置服务器配置文件
export function setServerConfig(name, config, callback, base_url='') {
  let data = {'name': name, 'config': config};
  post(base_url + '/v1/config', data, callback);
}