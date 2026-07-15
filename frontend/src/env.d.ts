/// <reference types="vite/client" />

declare module 'markdown-it' {
  import MarkdownIt from 'markdown-it'
  export default MarkdownIt
}

declare module 'highlight.js' {
  import hljs from 'highlight.js'
  export default hljs
}

declare module 'element-plus/dist/index.css' {
  const content: string
  export default content
}
