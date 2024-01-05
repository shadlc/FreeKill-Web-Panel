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
export function showCodeEditBox(msg, warning='', title='修改', text='', callback=null) {
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
    if(warning) {
        showDialog(warning, '提示', ()=>{
          callback(document.getElementById('code_edit_box').value);
          document.querySelectorAll('#code_edit_dialog').forEach((e)=>e.remove());
        });
    } else {
      callback(document.getElementById('code_edit_box').value);
      document.querySelectorAll('#code_edit_dialog').forEach((e)=>e.remove());
    }
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

// 输入一层字典套一层列表的数据生成对应表格
export function createTable(title, header, data, trans_table, show=true) {
  let table = document.createElement('table');
  let caption = document.createElement('caption');
  caption.style.cursor = 'pointer';
  if (!show) {
    caption.classList.add('hide-content');
    caption.innerHTML = caption.innerHTML.replace('▼', '▶');
  }
  caption.onclick = (e)=>{
    let self = e.target;
    console.log(e.which);
    if (self.classList.contains('hide-content')) {
      self.classList.remove('hide-content');
      caption.innerHTML = caption.innerHTML.replace('▶', '▼');
    } else {
      self.classList.add('hide-content');
      caption.innerHTML = caption.innerHTML.replace('▼', '▶');
    }
  }
  caption.textContent = title;
  table.appendChild(caption);
  let row = document.createElement('tr');
  for (let i in header) {
    let th = document.createElement('th');
    th.style.cursor = 'pointer';
    th.onclick = (e)=>{
      sortTable(e.target);
    }
    th.textContent = header[i];
    row.appendChild(th);
  }
  table.appendChild(row);
  for (let key in data) {
    row = document.createElement('tr');
    let cell = document.createElement('td');
    if (key in trans_table) {
      cell.textContent = trans_table[key];
      cell.title = key;
    } else {
      cell.textContent = key;
      cell.title = key;
    }
    row.appendChild(cell);
    for (let i = 0; i < data[key].length; i++) {
      cell = document.createElement('td');
      cell.textContent = data[key][i];
      row.appendChild(cell);
    }
    table.appendChild(row);
  }
  return table;
}

// 输入表格的一个表头元素,以这个表头对表进行排序
function sortTable(element) {
  let index = Array.from(element.parentNode.children).indexOf(element);
  let table = element.parentNode.parentNode;
  let order = 'asc';

  if (element.classList.contains('desc')) {
    element.classList.remove('desc');
    element.classList.add('asc');
    order = 'asc';
    element.innerHTML = element.innerHTML.replace('▲', '▼');
  } else if (element.classList.contains('asc')) {
    element.classList.add('desc');
    element.classList.remove('asc');
    order = 'desc';
    element.innerHTML = element.innerHTML.replace('▼', '▲');
  } else {
    Array.from(table.children[1].children).forEach((e)=>{
      if (e.tagName === "TH") {
        e.classList.remove('asc');
        e.classList.remove('desc');
        e.innerHTML = e.innerHTML.replace(/▼|▲/g, '');
      }
    })
    element.classList.add('asc');
    element.innerHTML = element.innerHTML + '▼';
  }

  let td_arr = [];
  let row_count = table.rows.length;
  for (let i = 1; i < row_count; i++) {
    let cell = table.rows[i].cells[index].innerHTML;
    td_arr.push(cell);
  }

  let is_all_numbers = td_arr.every(str => !isNaN(Number(str)));
  if (is_all_numbers) {
    td_arr = td_arr.map(str => Number(str));
  }

  for (let i = 0; i < row_count - 2; i++) {
    for (let j = 0; j < row_count - 2 - i; j++) {
      if (order == 'asc') {
        if (td_arr[j] < td_arr[j + 1]) {
          let temp = td_arr[j];
          td_arr[j] = td_arr[j + 1];
          td_arr[j + 1] = temp;
        }
      } else {
        if (td_arr[j] > td_arr[j + 1]) {
          let temp = td_arr[j];
          td_arr[j] = td_arr[j + 1];
          td_arr[j + 1] = temp;
        }
      }
    }
  }

  for (let item in td_arr) {
    for (let i = item; i < row_count; i++) {
      if (table.rows[i].cells[index].innerHTML == td_arr[item]) {
        table.insertBefore(table.rows[i], table.rows[parseInt(item)+1]);
        continue;
      };
    }
  }
}
