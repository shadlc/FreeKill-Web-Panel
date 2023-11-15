// 更改主题
export function setScheme(mode) {
  if (mode == 'light') {
    document.querySelector('html').style.colorScheme = 'light';
    color_scheme.classList.remove('dark');
  } else {
    document.querySelector('html').style.colorScheme = 'dark';
    color_scheme.classList.add('dark');
  }
}

// 弹出提示框
export function showDialog(msg, title='提示', callback=null) {
  let msg_div = `
  <div id="msg_dialog" class="modal">
    <div class="modal-dialog">
      <div class="mondal-title">
          <h3>`+title+`</h3>
          <span class="close-btn" onclick="document.getElementById('msg_dialog').remove();"></span>
      </div>
      <div class="modal-content center">
          <p1>`+msg+`</p1>
      </div>
      <div class="mondal-footer">
          <input id="msg_dialog_confirm_btn" class="btn" type="button" value="确定" onclick="document.getElementById('msg_dialog').remove();" />
      </div>
    </div>
  </div>
  `
  document.body.insertAdjacentHTML('BeforeEnd', msg_div);
  document.getElementById('msg_dialog_confirm_btn').addEventListener('click', callback);
}

// 计算时间间隔并返回格式化日期
export function period(now, past, format) {
  let milliseconds = Math.abs(now - past);
  let seconds = Math.floor(milliseconds / 1000);
  let minutes = Math.floor(seconds / 60);
  let hours = Math.floor(minutes / 60);
  let days = Math.floor(hours / 24);
  let months = Math.floor(days / 30);
  let years = Math.floor(months / 12);
  let result = format
    .replace('yyyy', years)
    .replace('MM', months % 12)
    .replace('dd', days % 30)
    .replace('HH', hours % 24)
    .replace('mm', minutes % 60)
    .replace('ss', seconds % 60);
  return result.trim();
}

// 获取新月杀最新版本号
// export function getFreeKillLatestVersion() {
//   fetch('https://gitee.com/notify-ctrl/FreeKill/releases/latest')
//   .then(response => {
//     if (response.ok) {
//       return response.url;
//     }
//   })
//   .then(url => {return console.log(url.split("/").pop());})
//   .catch(error => console.error(error));
//   return;
// }