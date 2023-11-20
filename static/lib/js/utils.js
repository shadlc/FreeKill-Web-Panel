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
      <div class="modal-title">
          <h3>`+title+`</h3>
          <span class="close-btn" onclick="document.getElementById('msg_dialog').remove();"></span>
      </div>
      <div class="modal-content center">
          <p1>`+msg+`</p1>
      </div>
      <div class="modal-footer">
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

// 对特定格式的时间进行计算
export function addSecondsToTime(time, add_seconds) {
  let [days, hours, minutes, seconds] = [0, 0, 0, 0]
  if(time.match(/^\d+:\d+$/g)) {
    [minutes, seconds] = time.match(/\d+/g).map(Number);
  } else if(time.match(/^\d+:\d+:\d+$/g)) {
    [hours, minutes, seconds] = time.match(/\d+/g).map(Number);
  } else if(time.match(/^\d+-\d+:\d+:\d+$/g)) {
    [days, hours, minutes, seconds] = time.match(/\d+/g).map(Number);
  }

  const total_seconds = (days*24*60*60) + (hours*60*60) + (minutes*60) + seconds;
  const updated_total_seconds = total_seconds + parseInt(add_seconds);
  const updated_days = Math.floor(updated_total_seconds / (24*60*60));
  const updated_hours = Math.floor(updated_total_seconds % (24*60*60) / (60*60)).toString().padStart(2, '0');
  const updated_minutes = Math.floor(updated_total_seconds % (60*60) / 60).toString().padStart(2, '0');
  const updated_seconds = Math.floor(updated_total_seconds % 60).toString().padStart(2, '0');

  if(days) {
    return `${updated_days}-${updated_hours}:${updated_minutes}:${updated_seconds}`;
  } else if(hours) {
    return `${updated_hours}:${updated_minutes}:${updated_seconds}`;
  } else {
    return `${updated_minutes}:${updated_seconds}`;
  }
}

// 转换BASH颜色为HTML实体
export function convertBashColor(text) {
  text = text.replace(/\[([0-9]{1,2}(;[0-9]{1,2})?)?m/g, (match, patten) => {
    let classes = '';
    if (patten) {
      if(patten == '0;0') {
        return '</span>';
      }
      let codes = patten.split(';');
        for (let i = 0; i < codes.length; i++) {
          let code = parseInt(codes[i]);
            switch (code) {
              case 30: classes += 'black'; break;
              case 31: classes += 'red'; break;
              case 32: classes += 'green'; break;
              case 33: classes += 'yellow'; break;
              case 34: classes += 'blue'; break;
              case 35: classes += 'magenta'; break;
              case 36: classes += 'cyan'; break;
              case 37: classes += 'white'; break;
              case 40: classes += 'bg-black'; break;
              case 41: classes += 'bg-red'; break;
              case 42: classes += 'bg-green'; break;
              case 43: classes += 'bg-yellow'; break;
              case 44: classes += 'bg-blue'; break;
              case 45: classes += 'bg-magenta'; break;
              case 46: classes += 'bg-cyan'; break;
              case 47: classes += 'bg-white'; break;
              default: break;
            }
            classes += ' '; // add space between classes
        }
      }
      return '<span class="' + classes.trim() + '">';
  });
  return text;
}

// 格式化文件大小
export function formatSize(value) {
  if (null == value || value == "") {
    return "0 Bytes";
  }
  const unitArray = new Array("B","KB","MB","GB","TB","PB","EB","ZB","YB");
  let index = 0;
  let srcSize = parseFloat(value * 1.1);
  index = Math.floor(Math.log(srcSize) / Math.log(1024));
  let size = srcSize/Math.pow(1024, index);
  size = size.toFixed(2);
  return size + unitArray[index];
}

// 获取新月杀最新版本号(域名不一致，不可实现)
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
