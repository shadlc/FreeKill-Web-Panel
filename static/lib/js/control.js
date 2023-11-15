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