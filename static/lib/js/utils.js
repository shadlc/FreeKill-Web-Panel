// 更改主题
export function changeScheme(mode) {
  if (mode != 'light' && mode != 'dark') {
    let scheme = getComputedStyle(document.querySelector('html')).colorScheme;
    if (scheme == 'light') {
      mode = 'dark';
    } else {
      mode = 'light'
    }
  }
  if (mode == 'light') {
    document.querySelector('html').style.colorScheme = 'light';
    color_scheme.classList.remove('dark');
  } else {
    document.querySelector('html').style.colorScheme = 'dark';
    color_scheme.classList.add('dark');
  }
}

// 弹出提示框
export function showDialog(msg, title='提示', callback=null, pre=false) {
  let msg_div = `
  <div id="msg_dialog" class="modal">
    <div class="modal-dialog">
      <div class="modal-title">
          <h3>`+title+`</h3>
          <span class="close-btn" onclick="document.querySelectorAll('#msg_dialog').forEach((e)=>e.remove());"></span>
      </div>
      <div class="modal-content center">
          <p1 style="overflow:auto;max-height:80vh;width:100%;text-align:center;">`+msg+`</p1>
      </div>
      <div class="modal-footer">
          <input id="msg_confirm_btn" class="btn" type="button" value="确定" onclick="document.querySelectorAll('#msg_dialog').forEach((e)=>e.remove());" />
      </div>
    </div>
  </div>
  `
  document.body.insertAdjacentHTML('BeforeEnd', msg_div);
  if (pre) {
    document.querySelectorAll('#msg_dialog p1').forEach((e)=>e.style.whiteSpace = 'pre-wrap');
  }
  document.getElementById('msg_confirm_btn').addEventListener('click', callback);
}

// 弹出处理框
export function showProcessingBox(msg, title='处理中', process=null) {
  let box_div = `
  <div id="process_dialog" class="modal">
    <div class="modal-dialog">
      <div class="modal-title">
          <h3>`+title+`</h3>
          <span class="close-btn" onclick="document.querySelectorAll('#process_dialog').forEach((e)=>e.remove());"></span>
      </div>
      <div class="modal-content center">
          <pre style="overflow:auto;max-height:80vh;max-width:90vw;word-wrap:break-word;white-space:pre-wrap;font-family:serif;margin:0;">`+msg+`</pre>
      </div>
      <div class="modal-footer">
          <i id="processing_icon" class="bi rotate"><b>&#xF130;</b></i>
          <input id="process_confirm_btn" class="btn hide" type="button" value="确定" onclick="document.querySelectorAll('#process_dialog').forEach((e)=>e.remove());" />
      </div>
    </div>
  </div>
  `
  document.body.insertAdjacentHTML('BeforeEnd', box_div);
  let pre = document.querySelector('#process_dialog pre');
  process(pre, (result)=>{
    if(result) {
      document.getElementById('processing_icon').remove();
      document.getElementById('process_confirm_btn').classList.remove('hide');
    } else {
      document.querySelectorAll('#process_dialog').forEach((e)=>e.remove());
    }
  })
}

// 弹出代码修改框
export function showCodeEditBox(msg, title='修改', text='', callback=null) {
  let box_div = `
  <div id="code_edit_dialog" class="modal">
    <div class="modal-dialog">
      <div class="modal-title">
          <h3>`+title+`</h3>
          <span class="close-btn" onclick="document.querySelectorAll('#code_edit_dialog').forEach((e)=>e.remove());"></span>
      </div>
      <div class="modal-content center">
          <p1 style="overflow: auto;">`+msg+`</p1>
          <textarea id="code_edit_box" class="code-editor">`+text+`</textarea>
      </div>
      <div class="modal-footer">
          <input id="code_edit_confirm_btn" class="btn" type="button" value="确定" />
      </div>
    </div>
  </div>
  `
  document.body.insertAdjacentHTML('BeforeEnd', box_div);
  document.getElementById('code_edit_box').style.height = (window.innerHeight - 200) + 'px';
  document.getElementById('code_edit_box').style.width = window.innerWidth - 70 + 'px';
  document.getElementById('code_edit_confirm_btn').addEventListener('click', ()=>{
    callback(document.getElementById('code_edit_box').value);
    document.querySelectorAll('#code_edit_dialog').forEach((e)=>e.remove());
  });
}

// 弹出文本输入框
export function showTextBox(msg, title='修改', callback=null) {
  let box_div = `
  <div id="text_dialog" class="modal">
    <div class="modal-dialog">
      <div class="modal-title">
          <h3>`+title+`</h3>
          <span class="close-btn" onclick="document.querySelectorAll('#text_dialog').forEach((e)=>e.remove());"></span>
      </div>
      <div class="modal-content center">
          <p1 style="overflow: auto;">`+msg+`</p1>
          <input id="text_box" class="text_input" type="text" style="margin-top:0.5rem;text-align:center;"></input>
      </div>
      <div class="modal-footer">
          <input id="text_confirm_btn" class="btn" type="button" value="确定" />
      </div>
    </div>
  </div>
  `
  document.body.insertAdjacentHTML('BeforeEnd', box_div);
  document.getElementById('text_confirm_btn').addEventListener('click', ()=>{
    callback(document.getElementById('text_box').value);
    document.querySelectorAll('#text_dialog').forEach((e)=>e.remove());
  });
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

// 给定时间戳返回格式化日期
export function formatTime(timestamp) {
  if(timestamp==0) {
    return 0;
  }
  let milliseconds = Math.abs(timestamp);
  let seconds = Math.floor(milliseconds / 1000);
  let minutes = Math.floor(seconds / 60);
  let hours = Math.floor(minutes / 60);
  let days = Math.floor(hours / 24);
  let months = Math.floor(days / 30);
  let years = Math.floor(months / 12);
  let string_time = (seconds % 60).toString().padStart(2, '0') + '秒';

  if(minutes != 0) {
    string_time = (minutes % 60).toString().padStart(2, '0') + '分' + string_time;
  } else return string_time;
  if(hours != 0) {
    string_time = (hours % 24).toString().padStart(2, '0') + '时' + string_time;
  } else return string_time;
  if(days != 0) {
    string_time = (days % 30).toString().padStart(2, '0') + '日' + string_time;
  } else return string_time;
  if(months != 0) {
    string_time = (months % 12).toString().padStart(2, '0') + '月' + string_time;
  } else return string_time;
  if(years != 0) {
    string_time = years.toString().padStart(2, '0') + '年' + string_time;
  } else return string_time;
  return string_time;
}

// 对特定格式的时间进行计算
export function addSecondsToTime(time, add_seconds) {
  let [days, hours, minutes, seconds] = [0, 0, 0, 0]
  if(time.match(/^\d+秒$/g)) {
    [seconds] = time.match(/\d+/g).map(Number);
  } else if(time.match(/^\d+分\d+秒$/g)) {
    [minutes, seconds] = time.match(/\d+/g).map(Number);
  } else if(time.match(/^\d+时\d+分\d+秒$/g)) {
    [hours, minutes, seconds] = time.match(/\d+/g).map(Number);
  } else if(time.match(/^\d+日\d+时\d+分\d+秒$/g)) {
    [days, hours, minutes, seconds] = time.match(/\d+/g).map(Number);
  } else {
    return time
  }

  const total_seconds = (days*24*60*60) + (hours*60*60) + (minutes*60) + seconds;
  const updated_total_seconds = total_seconds + parseInt(add_seconds);
  const updated_days = Math.floor(updated_total_seconds / (24*60*60));
  const updated_hours = Math.floor(updated_total_seconds % (24*60*60) / (60*60)).toString().padStart(2, '0');
  const updated_minutes = Math.floor(updated_total_seconds % (60*60) / 60).toString().padStart(2, '0');
  const updated_seconds = Math.floor(updated_total_seconds % 60).toString().padStart(2, '0');

  if(updated_days != '00') {
    return `${updated_days}日${updated_hours}时${updated_minutes}分${updated_seconds}秒`;
  } else if(updated_hours != '00') {
    return `${updated_hours}时${updated_minutes}分${updated_seconds}秒`;
  } else if(updated_minutes != '00') {
    return `${updated_minutes}分${updated_seconds}秒`;
  } else {
    return `${updated_seconds}秒`;
  }
}

// 对特定格式的时间计算得到时间戳
export function timeToTimeStamp(time) {
  let [days, hours, minutes, seconds] = [0, 0, 0, 0]
  if(time.match(/^\d+秒$/g)) {
    [seconds] = time.match(/\d+/g).map(Number);
  } else if(time.match(/^\d+分\d+秒$/g)) {
    [minutes, seconds] = time.match(/\d+/g).map(Number);
  } else if(time.match(/^\d+时\d+分\d+秒$/g)) {
    [hours, minutes, seconds] = time.match(/\d+/g).map(Number);
  } else if(time.match(/^\d+日\d+时\d+分\d+秒$/g)) {
    [days, hours, minutes, seconds] = time.match(/\d+/g).map(Number);
  }
  return (days*24*60*60) + (hours*60*60) + (minutes*60) + seconds;
}

// 转换BASH颜色为HTML实体
export function convertBashColor(text) {
  let color_matched = 0;
  text = text.replace(/\[([0-9]{1,2}(;[0-9]{1,2})?)?m/g, (match, patten) => {
    let classes = '';
    if (patten) {
      if(patten == '0;0') {
        color_matched -= 1;
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
      color_matched += 1;
      return '<span class="' + classes.trim() + '">';
  });
  if(color_matched > 0) {
    text += '</span>';
  }
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

// 获取新月杀最新版本号(不允许跨域访问，不可实现)
// export function getFreeKillLatestVersion() {
//   fetch('https://github.com/notify-ctrl/FreeKill/releases/latest')
//   .then(response => {
//     if (response.ok) {
//       return response.url;
//     }
//   })
//   .then(url => {return console.log(url.split("/").pop());})
//   .catch(error => console.error(error));
//   return;
// }
