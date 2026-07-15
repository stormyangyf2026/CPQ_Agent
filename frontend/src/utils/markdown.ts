import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.min.css'

// 初始化 markdown-it
const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
  breaks: true,
  highlight: function (str: string, lang: string): string {
    if (lang && hljs.getLanguage(lang)) {
      try {
        const highlighted = hljs.highlight(str, {
          language: lang,
          ignoreIllegals: true,
        })
        const languageLabel = lang || ''
        return (
          `<div class="code-block-header">` +
          `<span class="code-lang">${languageLabel}</span>` +
          `<button class="copy-btn" onclick="(function(){` +
          `const el=document.createElement('textarea');` +
          `el.value=this.parentElement.nextElementSibling.textContent;` +
          `document.body.appendChild(el);` +
          `el.select();document.execCommand('copy');` +
          `document.body.removeChild(el);` +
          `this.textContent='已复制';` +
          `setTimeout(()=>{this.textContent='复制'},2000)` +
          `})()">复制</button>` +
          `</div>` +
          `<pre class="hljs"><code>${highlighted.value}</code></pre>`
        )
      } catch {
        // fallback
      }
    }

    // 无语言或 highlight 失败时
    const escaped = md.utils?.escapeHtml?.(str) || escapeHtml(str)
    return `<pre class="hljs"><code>${escaped}</code></pre>`
  },
})

// 简易 HTML 转义
function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

/**
 * 将 Markdown 文本渲染为 HTML
 */
export function renderMarkdown(content: string): string {
  if (!content) return ''
  try {
    return md.render(content)
  } catch (err) {
    console.error('Markdown 渲染失败:', err)
    return `<p>${escapeHtml(content)}</p>`
  }
}
