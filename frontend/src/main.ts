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
createApp(App).mount('#app')
