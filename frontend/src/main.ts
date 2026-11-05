import { createApp } from 'vue'
import App from './App.vue'
import { config } from 'md-editor-v3'
import katex from 'katex'
import hljs from 'highlight.js'
import 'katex/dist/katex.min.css'
import 'highlight.js/styles/github.css'
import githubStyle from 'highlight.js/styles/github.css?url'
import './style.css'
config({ editorExtensions: { katex: { instance: katex, css: '' }, highlight: { instance: hljs, css: { atom: { light: githubStyle, dark: githubStyle } } } } })
// Let the desktop WebView open external destinations in the system browser.
document.addEventListener('click', (event) => {
  const target = event.target
  if (!(target instanceof Element)) return
  const link = target.closest('a[href]') as HTMLAnchorElement | null
  if (!link) return
  try {
    const url = new URL(link.href, location.href)
    if ((url.protocol === 'http:' || url.protocol === 'https:') && url.origin !== location.origin) {
      link.target = '_blank'
      link.rel = 'noopener noreferrer'
    }
  } catch { /* Ignore invalid URLs. */ }
}, true)
createApp(App).mount('#app')
