# CPQ Agent App 前端实现方案

> **项目**：AI 配单桌面 App — 独立运行的 AI CPQ 桌面应用
> **版本**：v1.0
> **日期**：2026-07-05
> **技术栈**：Vue 3 + Composition API + TypeScript + Element Plus + Vite + Pinia + markdown-it + Fetch SSE

---

## 目录

1. [项目脚手架方案](#1-项目脚手架方案)
2. [路由设计](#2-路由设计)
3. [SSE 流式通信层](#3-sse-流式通信层)
4. [Markdown 渲染增强](#4-markdown-渲染增强)
5. [关键功能实现方案](#5-关键功能实现方案)
6. [错误处理](#6-错误处理)
7. [打包部署](#7-打包部署)
8. [PWA 配置](#8-pwa-配置)

---

## 1. 项目脚手架方案

### 1.1 完整目录结构

```
cpq-agent-app/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tsconfig.node.json
├── .env                          # 公共环境变量
├── .env.development              # 开发环境
├── .env.production               # 生产环境
├── .eslintrc.cjs
├── .prettierrc
├── postcss.config.js
├── tailwind.config.js
├── index.html
│
├── electron/
│   ├── main.ts
│   ├── preload.ts
│   └── electron-builder.yml
│
├── public/
│   ├── favicon.ico
│   ├── manifest.json
│   ├── robots.txt
│   ├── logo.svg
│   ├── logo-192.png
│   └── logo-512.png
│
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── env.d.ts
│   │
│   ├── router/
│   │   ├── index.ts
│   │   └── guards.ts
│   │
│   ├── stores/
│   │   ├── index.ts
│   │   ├── chat.ts
│   │   ├── session.ts
│   │   ├── settings.ts
│   │   ├── config.ts
│   │   └── sse.ts
│   │
│   ├── services/
│   │   ├── sse.ts
│   │   ├── api.ts
│   │   └── retry.ts
│   │
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatMessages.vue
│   │   │   ├── ChatMessage.vue
│   │   │   ├── ChatInput.vue
│   │   │   └── TypingEffect.vue
│   │   │
│   │   ├── markdown/
│   │   │   ├── MarkdownRenderer.vue
│   │   │   ├── CpqProductCard.vue
│   │   │   ├── CpqBomTable.vue
│   │   │   ├── CpqComparePanel.vue
│   │   │   ├── CpqStatusBadge.vue
│   │   │   └── CpqInlineAction.vue
│   │   │
│   │   ├── common/
│   │   │   ├── LoadingSpinner.vue
│   │   │   ├── ErrorAlert.vue
│   │   │   ├── EmptyState.vue
│   │   │   ├── ConnectionStatus.vue
│   │   │   └── ConfirmDialog.vue
│   │   │
│   │   └── layout/
│   │       ├── AppLayout.vue
│   │       ├── Sidebar.vue
│   │       ├── HeaderBar.vue
│   │       └── StatusFooter.vue
│   │
│   ├── views/
│   │   ├── ChatView.vue
│   │   ├── HistoryView.vue
│   │   ├── SettingsView.vue
│   │   ├── BomsView.vue
│   │   ├── CompareView.vue
│   │   └── NotFoundView.vue
│   │
│   ├── composables/
│   │   ├── useSse.ts
│   │   ├── useChat.ts
│   │   ├── useTyping.ts
│   │   ├── useMarkdown.ts
│   │   ├── useBomTable.ts
│   │   ├── useCompareDiff.ts
│   │   ├── useAutoSave.ts
│   │   └── useElectron.ts
│   │
│   ├── utils/
│   │   ├── markdown.ts
│   │   ├── markdown-rules.ts
│   │   ├── format.ts
│   │   ├── debounce.ts
│   │   └── constants.ts
│   │
│   ├── assets/
│   │   ├── styles/
│   │   │   ├── variables.scss
│   │   │   ├── global.scss
│   │   │   ├── markdown.scss
│   │   │   ├── chat.scss
│   │   │   ├── transition.scss
│   │   │   └── theme-override.scss
│   │   └── icons/
│   │       └── index.ts
│   │
│   └── types/
│       ├── chat.ts
│       ├── sse.ts
│       ├── settings.ts
│       ├── bom.ts
│       ├── product.ts
│       └── cpq.ts
│
├── sw.ts
├── sw-register.ts
│
└── scripts/
    └── verify-electron.ts
```

### 1.2 package.json 完整依赖清单

```jsonc
{
  "name": "cpq-agent-app",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc --noEmit && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .vue,.ts,.tsx --fix",
    "format": "prettier --write src/",
    "electron:dev": "vite & electron .",
    "electron:build": "vite build && electron-builder",
    "type-check": "vue-tsc --noEmit"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0",
    "pinia": "^2.1.0",
    "element-plus": "^2.7.0",
    "@element-plus/icons-vue": "^2.3.0",
    "markdown-it": "^14.0.0",
    "markdown-it-anchor": "^9.0.0",
    "markdown-it-task-lists": "^2.1.0",
    "highlight.js": "^11.9.0",
    "diff": "^5.2.0",
    "dompurify": "^3.1.0",
    "uuid": "^9.0.0",
    "workbox-precaching": "^7.1.0",
    "workbox-routing": "^7.1.0",
    "workbox-strategies": "^7.1.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.2.0",
    "vite-plugin-pwa": "^0.19.0",
    "vite-plugin-electron": "^0.28.0",
    "vite-plugin-electron-renderer": "^0.14.0",
    "typescript": "^5.4.0",
    "vue-tsc": "^2.0.0",
    "@vue/tsconfig": "^0.5.0",
    "eslint": "^8.57.0",
    "@vue/eslint-config-typescript": "^13.0.0",
    "eslint-plugin-vue": "^9.24.0",
    "prettier": "^3.2.0",
    "sass": "^1.72.0",
    "electron": "^29.0.0",
    "electron-builder": "^24.13.0",
    "@types/markdown-it": "^13.0.0",
    "@types/diff": "^5.2.0",
    "@types/dompurify": "^3.0.0",
    "@types/uuid": "^9.0.0",
    "@types/node": "^20.11.0"
  }
}
```

### 1.3 vite.config.ts 关键配置

```typescript
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { VitePWA } from 'vite-plugin-pwa'
import electron from 'vite-plugin-electron'
import renderer from 'vite-plugin-electron-renderer'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [
      vue(),

      // Electron 支持（桌面端时启用）
      ...(env.VITE_TARGET === 'electron'
        ? [
            electron([
              {
                entry: 'electron/main.ts',
                vite: { build: { outDir: 'dist-electron', rollupOptions: { external: ['electron'] } } },
              },
              { entry: 'electron/preload.ts', onstart(args) { args.reload() } },
            ]),
            renderer(),
          ]
        : []),

      // PWA 支持
      VitePWA({
        registerType: 'autoUpdate',
        includeAssets: ['logo.svg', 'logo-192.png', 'logo-512.png'],
        manifest: {
          name: 'CPQ Agent App',
          short_name: 'CPQ Agent',
          description: 'AI 配单桌面应用',
          theme_color: '#1a56db',
          background_color: '#ffffff',
          display: 'standalone',
          icons: [
            { src: 'logo-192.png', sizes: '192x192', type: 'image/png' },
            { src: 'logo-512.png', sizes: '512x512', type: 'image/png' },
          ],
        },
        workbox: {
          globPatterns: ['**/*.{js,css,html,svg,png,ico,woff2}'],
          runtimeCaching: [
            {
              urlPattern: /^https:\/\/api\.*/i,
              handler: 'NetworkFirst',
              options: { cacheName: 'api-cache', expiration: { maxEntries: 50, maxAgeSeconds: 60 * 60 * 24 } },
            },
          ],
        },
      }),
    ],

    resolve: { alias: { '@': resolve(__dirname, 'src'), '#': resolve(__dirname, 'types') } },
    server: {
      port: 5173,
      proxy: {
        '/api': { target: env.VITE_API_BASE_URL || 'http://localhost:8000', changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, '') },
        '/sse': { target: env.VITE_SSE_URL || 'http://localhost:8000', changeOrigin: true, ws: true },
      },
    },
    build: {
      target: 'esnext', outDir: 'dist', sourcemap: false,
      rollupOptions: {
        output: {
          manualChunks: {
            'vue-vendor': ['vue', 'vue-router', 'pinia'],
            'element-plus': ['element-plus', '@element-plus/icons-vue'],
            'markdown-vendor': ['markdown-it', 'highlight.js'],
          },
        },
      },
      chunkSizeWarningLimit: 1000,
    },
    css: { preprocessorOptions: { scss: { additionalData: `@use "@/assets/styles/variables.scss" as *;` } } },
  }
})
```

### 1.4 tsconfig.json 关键配置

```jsonc
{
  "compilerOptions": {
    "target": "ESNext", "module": "ESNext", "moduleResolution": "bundler",
    "strict": true, "jsx": "preserve", "resolveJsonModule": true,
    "isolatedModules": true, "esModuleInterop": true,
    "lib": ["ESNext", "DOM", "DOM.Iterable"], "skipLibCheck": true, "noEmit": true,
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"], "#/*": ["types/*"] },
    "types": ["vite/client", "element-plus/global", "node"]
  },
  "include": ["src/**/*.ts", "src/**/*.vue", "src/**/*.d.ts", "types/**/*.d.ts"],
  "exclude": ["node_modules", "dist", "dist-electron"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

---

## 2. 路由设计

### 2.1 路由表

```typescript
import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/chat' },
  { path: '/chat', name: 'Chat', component: () => import('@/views/ChatView.vue'), meta: { title: 'AI 配单对话', keepAlive: true } },
  { path: '/chat/:sessionId', name: 'ChatSession', component: () => import('@/views/ChatView.vue'), props: true, meta: { title: '会话', keepAlive: true } },
  { path: '/history', name: 'History', component: () => import('@/views/HistoryView.vue'), meta: { title: '历史会话' } },
  { path: '/boms', name: 'Boms', component: () => import('@/views/BomsView.vue'), meta: { title: 'BOM 清单' } },
  { path: '/boms/:bomId', name: 'BomDetail', component: () => import('@/views/BomsView.vue'), props: true, meta: { title: 'BOM 详情' } },
  { path: '/compare', name: 'Compare', component: () => import('@/views/CompareView.vue'), meta: { title: '方案对比' } },
  { path: '/settings', name: 'Settings', component: () => import('@/views/SettingsView.vue'), meta: { title: '设置' } },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/views/NotFoundView.vue'), meta: { title: '404' } },
]

const router = createRouter({
  history: createWebHashHistory(), // 桌面应用用 hash 路由，避免 Electron 的 file:// 协议问题
  routes,
  scrollBehavior() { return { top: 0 } },
})
export default router
```

### 2.2 路由守卫

```typescript
// src/router/guards.ts
import type { Router } from 'vue-router'
import { useSSEStore } from '@/stores/sse'
import { useSettingsStore } from '@/stores/settings'
import { ElMessage, ElMessageBox } from 'element-plus'

export function setupRouterGuards(router: Router): void {
  router.beforeEach((to, _from, next) => {
    document.title = to.meta.title ? `${to.meta.title} - CPQ Agent App` : 'CPQ Agent App'
    next()
  })
  router.beforeEach((to, _from, next) => {
    const agent = useSSEStore()
    if (to.meta.requiresAgent && !agent.isConnected) {
      agent.reconnect()
      ElMessage.warning('正在连接 Agent 服务...')
      next(false); return
    }
    next()
  })
  router.beforeEach((to, _from, next) => {
    const s = useSettingsStore()
    if (s.isDirty && to.name !== 'Settings') {
      ElMessageBox.confirm('设置未保存，确定离开？', '', { type: 'warning' })
        .then(() => { s.resetDirty(); next() }).catch(() => next(false))
      return
    }
    next()
  })
}
```

---

## 3. SSE 流式通信层

### 3.1 为什么不用 EventSource

| 对比项 | EventSource | Fetch + ReadableStream |
|--------|------------|----------------------|
| HTTP 方法 | 仅 GET | 任意（POST 传递 Agent 上下文） |
| 自定义请求头 | ❌ 不支持 | ✅ Authorization、Session-Id |
| 超时控制 | ❌ | ✅ AbortController + 定时器 |
| 重连策略 | 固定间隔不可控 | ✅ 指数退避 + 抖动 |
| 缓冲区防溢出 | 无 | ✅ 1MB 上限保护 |
| 传输二进制 | ❌ | ✅ |

### 3.2 SSE 通信核心 (src/services/sse.ts)

```typescript
import { v4 as uuid } from 'uuid'

export type SSEEventType =
  | 'message_start' | 'message_delta' | 'message_stop' | 'error'
  | 'tool_call_start' | 'tool_call_end' | 'status'
  | 'bom_update' | 'config_update' | 'heartbeat' | 'complete'

export interface SSEEvent { id: string; type: SSEEventType; data: unknown; timestamp: number; traceId?: string }
export interface SSEOptions { url: string; body: unknown; method?: 'POST'; headers?: Record<string, string>; signal?: AbortSignal; timeout?: number }

export class SSEError extends Error { constructor(m: string) { super(m); this.name = 'SSEError' } }
export class SSEDeliveryError extends SSEError {
  code: number
  constructor(code: number, m: string) { super(`SSE delivery (${code}): ${m}`); this.name = 'SSEDeliveryError'; this.code = code }
}
export class SSETimeoutError extends SSEError {
  constructor(ms: number) { super(`SSE timeout ${ms}ms`); this.name = 'SSETimeoutError' }
}

const TERM = '\n\n', MAX_BUF = 1024 * 1024

/**
 * 核心：fetch POST → ReadableStream → TextDecoder → \n\n 拆分 → yield SSEEvent
 */
export async function* sseStream(opts: SSEOptions): AsyncGenerator<SSEEvent> {
  const { url, body, method = 'POST', headers = {}, signal, timeout = 120_000 } = opts
  const ctrl = new AbortController()
  const tid = setTimeout(() => ctrl.abort(new SSETimeoutError(timeout)), timeout)
  const sig = signal ? combineSignals(signal, ctrl.signal) : ctrl.signal

  try {
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream', 'Cache-Control': 'no-cache', ...headers },
      body: JSON.stringify(body), signal: sig,
    })
    if (!res.ok) throw new SSEDeliveryError(res.status, res.statusText)
    if (!res.body) throw new SSEError('No response body')

    const reader = res.body.getReader()
    const dec = new TextDecoder()
    let buf = ''

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buf += dec.decode(value, { stream: true })
        if (buf.length > MAX_BUF) buf = buf.slice(-MAX_BUF / 2)

        const parts = buf.split(TERM)
        buf = parts.pop() || ''
        for (const p of parts) {
          if (!p.trim()) continue
          const ev = parseLine(p)
          if (ev) yield ev
        }
      }
      if (buf.trim()) { const ev = parseLine(buf); if (ev) yield ev }
    } finally { reader.releaseLock() }
  } finally { clearTimeout(tid) }
}

/** SSE 协议行解析 */
function parseLine(text: string): SSEEvent | null {
  const lines = text.split('\n')
  let type = 'message', data = '', id = '', trace = ''
  for (const l of lines) {
    if (l.startsWith('event: ')) type = l.slice(7).trim()
    else if (l.startsWith('data: ')) data += l.slice(6)
    else if (l.startsWith('id: ')) id = l.slice(4).trim()
    else if (l.startsWith('trace: ')) trace = l.slice(7).trim()
  }
  if (!data) return null
  let parsed: unknown
  try { parsed = JSON.parse(data) } catch { parsed = data }
  return { id: id || uuid(), type: type as SSEEventType, data: parsed, timestamp: Date.now(), traceId: trace || undefined }
}

function combineSignals(...sigs: AbortSignal[]): AbortSignal {
  const c = new AbortController()
  for (const s of sigs) {
    if (s.aborted) { c.abort(s.reason); return c.signal }
    s.addEventListener('abort', () => c.abort(s.reason), { once: true })
  }
  return c.signal
}
```

### 3.3 断线重连 (src/services/retry.ts)

```typescript
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  opts: { maxRetries?: number; baseDelay?: number; maxDelay?: number; jitterFactor?: number } = {}
): Promise<T> {
  const { maxRetries = 5, baseDelay = 1000, maxDelay = 30000, jitterFactor = 0.3 } = opts
  for (let i = 0; i <= maxRetries; i++) {
    try { return await fn() }
    catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') throw err
      const te = err as { constructor: { name: string }; code?: number }
      if (te.constructor?.name === 'SSEDeliveryError' && te.code != null && te.code >= 400 && te.code < 500) throw err
      if (i >= maxRetries) throw err
      const d = Math.min(baseDelay * Math.pow(2, i), maxDelay)
      const j = d * jitterFactor * (Math.random() * 2 - 1)
      await new Promise(r => setTimeout(r, Math.round(d + j)))
    }
  }
  throw new Error('Unexpected')
}
```

### 3.4 useSse 组合式函数

```typescript
// src/composables/useSse.ts
import { ref, onUnmounted } from 'vue'
import { sseStream } from '@/services/sse'
import { retryWithBackoff } from '@/services/retry'

export function useSSE() {
  const isStreaming = ref(false)
  const abortController = ref<AbortController | null>(null)

  async function startStream(
    payload: { sessionId: string; message: string; config?: Record<string, unknown> },
    cbs: { onDelta: (c: string) => void; onToolCall: (n: string, a: unknown) => void; onToolResult: (n: string, r: string) => void; onStatus: (m: string) => void; onComplete: (t: string) => void; onError: (e: Error) => void }
  ) {
    if (isStreaming.value) return
    isStreaming.value = true
    abortController.value = new AbortController()
    let fullText = ''

    try {
      await retryWithBackoff(async () => {
        for await (const ev of sseStream({
          url: '/api/agent/chat',
          body: { session_id: payload.sessionId, message: payload.message, config: payload.config, stream: true },
          signal: abortController.value?.signal, timeout: 180_000,
          headers: { 'X-Session-Id': payload.sessionId },
        })) {
          switch (ev.type) {
            case 'message_delta': { const c = (ev.data as { content: string }).content; fullText += c; cbs.onDelta(c); break }
            case 'message_stop': cbs.onComplete(fullText); break
            case 'tool_call_start': { const { name, args } = ev.data as { name: string; args: unknown }; cbs.onToolCall(name, args); break }
            case 'tool_call_end': { const { name, result } = ev.data as { name: string; result: string }; cbs.onToolResult(name, result); break }
            case 'status': cbs.onStatus((ev.data as { message: string }).message); break
            case 'error': throw new Error((ev.data as { message: string }).message || 'Agent 错误')
            case 'heartbeat': break
          }
        }
      }, { maxRetries: 3, baseDelay: 2000 })
    } catch (err) {
      if ((err as Error).name !== 'AbortError') cbs.onError(err as Error)
    } finally { isStreaming.value = false }
  }

  function abortStream() { abortController.value?.abort(); isStreaming.value = false }
  onUnmounted(() => abortStream())
  return { isStreaming, startStream, abortStream }
}
```

---

## 4. Markdown 渲染增强

### 4.1 markdown-it 配置 (src/utils/markdown.ts)

```typescript
import MarkdownIt from 'markdown-it'
import anchor from 'markdown-it-anchor'
import taskLists from 'markdown-it-task-lists'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'
import { customRules } from './markdown-rules'

export function createMarkdownRenderer(): MarkdownIt {
  const md = new MarkdownIt({
    html: true, linkify: true, typographer: true,
    highlight: (str: string, lang: string): string => {
      if (lang && hljs.getLanguage(lang)) {
        try {
          return `<pre class="hljs"><code class="language-${lang}">${
            hljs.highlight(str, { language: lang, ignoreIllegals: true }).value
          }</code></pre>`
        } catch {}
      }
      return `<pre class="hljs"><code>${escapeHtml(str)}</code></pre>`
    },
  })
  md.use(anchor, { permalink: anchor.permalink.headerLink(), level: [1, 2, 3] })
  md.use(taskLists, { enabled: true, label: true, labelAfter: true })
  customRules.forEach(r => md.use(r.plugin, r.options))
  return md
}

export function renderMarkdown(md: MarkdownIt, text: string): string {
  return DOMPurify.sanitize(md.render(text), {
    ALLOWED_TAGS: ['p','br','strong','em','del','ins','u','h1','h2','h3','h4','h5','h6',
      'ul','ol','li','table','thead','tbody','tr','th','td','pre','code','blockquote',
      'a','img','hr','span','div','section','input'],
    ALLOWED_ATTR: ['href','target','rel','src','alt','title','class','id','style','data-*','checked','disabled','type'],
    ALLOW_DATA_ATTR: true,
  })
}

function escapeHtml(s: string): string {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')
}
```

### 4.2 自定义渲染规则设计 (src/utils/markdown-rules.ts)

**设计思路**：Agent 按约定格式输出特殊块，markdown-it 自定义容容器规则将原始内容解析为带 `data-cpq-component` 属性的 `<div>`。MarkdownRenderer.vue 组件渲染后，通过 `onMounted` 查询这些标记并替换为对应的 Vue 组件。

**Agent 输出约定格式**：

```markdown
::: product-card
{"id":"PRD-001","name":"工业变频器 VFD-5000","spec":"380V/50Hz/75kW","price":28500,"stock":12}
:::

::: bom-table bomId="BOM-20260705"
| 物料编码 | 名称 | 规格 | 数量 | 单价 |
|---------|------|------|------|------|
| MAT-001 | 电机 75kW | M1 | 2 | 12000 |
:::

::: compare-panel schemeA="方案A-基础型" schemeB="方案B-增强型"
| 项目 | 方案A | 方案B |
|------|-------|-------|
| 价格 | 85000 | 125000 |
:::

::: badge success "已确认" :::

::: action confirm_bom "采纳此BOM" data='{"bomId":"BOM-20260705"}' :::
```

**自定义容器 rule 注入方式**（以 product-card 为例）：

```typescript
// markdown-it 插件：解析 ::: product-card 容器块
export function cpqProductCardPlugin(md: MarkdownIt): void {
  md.block.ruler.before('fence', 'cpq_product_card', (state, startLine, endLine, silent) => {
    const pos = state.bMarks[startLine] + state.tShift[startLine]
    const line = state.src.slice(pos, state.eMarks[startLine]).trim()
    if (!line.startsWith('::: product-card')) return false
    if (silent) return true

    // 找到结束 :::
    let end = startLine + 1
    while (end < endLine) {
      const p = state.bMarks[end] + state.tShift[end]
      if (state.src.slice(p, state.eMarks[end]).trim() === ':::') break
      end++
    }

    const content = state.src.slice(
      state.bMarks[startLine + 1] + state.tShift[startLine + 1],
      state.eMarks[end - 1]
    )

    state.tokens.push({
      type: 'cpq_product_card_open', tag: 'div',
      attrs: [['data-cpq-component', 'product-card'], ['data-cpq-payload', content.trim()]],
      map: [startLine, end + 1], nesting: 1, level: state.level,
      children: [], content: '', markup: ':::', info: '', block: true, hidden: false,
    })
    state.tokens.push({
      type: 'cpq_product_card_close', tag: 'div',
      nesting: -1, level: state.level,
      children: [], content: '', markup: ':::', info: '', block: true, hidden: false,
    })
    state.line = end + 1
    return true
  })
}
```

### 4.3 MarkdownRenderer.vue 组件（组件挂载桥接）

```vue
<!-- src/components/markdown/MarkdownRenderer.vue -->
<template>
  <div ref="container" class="cpq-markdown" v-html="renderedHtml"></div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { createMarkdownRenderer, renderMarkdown } from '@/utils/markdown'
import CpqProductCard from './CpqProductCard.vue'
import CpqBomTable from './CpqBomTable.vue'
import CpqComparePanel from './CpqComparePanel.vue'
import CpqStatusBadge from './CpqStatusBadge.vue'
import CpqInlineAction from './CpqInlineAction.vue'

const props = defineProps<{ text: string }>()
const container = ref<HTMLElement | null>(null)
const md = createMarkdownRenderer()

const renderedHtml = computed(() => renderMarkdown(md, props.text))

/** 组件标签名 → Vue 组件定义 */
const componentMap: Record<string, any> = {
  'product-card': CpqProductCard,
  'bom-table': CpqBomTable,
  'compare-panel': CpqComparePanel,
  'status-badge': CpqStatusBadge,
  'inline-action': CpqInlineAction,
}

/** 渲染后挂载自定义 Vue 组件 */
async function mountComponents() {
  if (!container.value) return
  const els = container.value.querySelectorAll<HTMLElement>('[data-cpq-component]')
  for (const el of els) {
    const name = el.dataset.cpqComponent
    if (!name || !componentMap[name]) continue
    const Component = componentMap[name]
    // 将 data-* 属性作为 props 传入
    const props: Record<string, string> = {}
    for (const attr of el.attributes) {
      if (attr.name.startsWith('data-cpq-')) {
        props[attr.name.replace('data-cpq-', '')] = attr.value
      }
    }
    // 创建挂载点
    const mountPoint = document.createElement('span')
    el.parentNode?.replaceChild(mountPoint, el)
    // 使用 createApp 动态挂载
    const { createApp } = await import('vue')
    const app = createApp(Component, { ...props })
    app.mount(mountPoint)
  }
}

watch(() => props.text, async () => {
  await nextTick()
  mountComponents()
})

onMounted(async () => {
  await nextTick()
  mountComponents()
})
</script>
```

---

## 5. 关键功能实现方案

### 5.1 打字机流式效果 (src/composables/useTyping.ts + TypingEffect.vue)

**设计要点**：
1. **流式输入分两阶段**：
   - **Phase 1 — 纯文本累加**（SSE 实时读取）：收到 chunk 后直接追加到 accumulatedText
   - **Phase 2 — 打字机视觉输出**（定时器控制）：从 accumulatedText 中逐个字符取出，遇到 Markdown 标记（如 `**`、`[`, `]`、`(`, `)`、`<table>` 等）时整段跳过
2. **Markdown 标记检测**：tokenizer 需要识别完整的 Markdown token 边界，一次性输出整段格式标记而不逐字符卡顿
3. **光标闪烁**：使用 CSS animation `@keyframes blink` 实现

```typescript
// src/composables/useTyping.ts
import { ref, computed, watch, type Ref } from 'vue'

export interface TypingOptions {
  charsPerTick?: number    // 每次 tick 输出的字符数（默认 3-5 随机的自然感）
  tickInterval?: number    // tick 间隔（默认 30-60ms）
  onTick?: (current: string) => void
}

/**
 * 打字机效果组合式函数
 * 
 * 核心挑战：Markdown 标记不能逐字符输出——会导致渲染闪烁
 * 解决方案：实现一个 MarkdownTokenizer 识别 token 边界，整 token 输出
 */
export function useTyping(
  accumulatedText: Ref<string>,
  options: TypingOptions = {}
) {
  const { tickInterval = 40, charsPerTick = 4 } = options

  const displayedText = ref('')        // 当前已打出的文本（准备渲染）
  const isTyping = ref(false)
  const cursorIdx = ref(0)            // 已输出的字符索引
  const typedComplete = computed(() => cursorIdx.value >= accumulatedText.value.length)


  /** Markdown token 边界识别 — 一次性跳过整个格式化标记，避免渲染闪烁 */
  const mdTokenPatterns = [
    /^\*\*[^*]+\*\*/,           // **bold**
    /^\*[^*]+\*/,               // *italic*
    /^~~[^~]+~~/,               // ~~strike~~
    /^`[^`]+`/,                 // inline code
    /^```[\s\S]*?```/,          // code block
    /^\[([^\]]+)\]\(([^)]+)\)/, // [link](url)
    /^!\[([^\]]*)\]\(([^)]+)\)/,// ![image](url)
    /^#{1,6}\s+/,               // heading markers
    /^>\s+/,                    // blockquote
    /^-{3,}$/,                  // hr
    /^\|.*\|$/,                 // table row
    /^:::.*/,                   // custom container
    /^\s*[-*+]\s+/,             // list marker
    /^\s*\d+\.\s+/,             // ordered list
  ]

  function findNextToken(fromIdx: number): number {
    const remaining = accumulatedText.value.slice(fromIdx)
    for (const pattern of mdTokenPatterns) {
      const m = remaining.match(pattern)
      if (m) return fromIdx + m[0].length
    }
    return fromIdx + 1 // 普通字符
  }

  /** 启动打字机 */
  function startTyping() {
    if (isTyping.value) return
    isTyping.value = true
    cursorIdx.value = displayedText.value.length

    const tick = () => {
      if (cursorIdx.value >= accumulatedText.value.length) {
        displayedText.value = accumulatedText.value
        isTyping.value = false
        return
      }

      // 每次 tick 输出多个字符（速度控制：随机 2~6 个字符的自然节奏感）
      const batchSize = Math.floor(Math.random() * 5) + 2
      for (let i = 0; i < batchSize; i++) {
        if (cursorIdx.value >= accumulatedText.value.length) break
        // 识别 Markdown token 边界，整 token 跳跃
        const nextIdx = findNextToken(cursorIdx.value)
        cursorIdx.value = nextIdx
      }

      displayedText.value = accumulatedText.value.slice(0, cursorIdx.value)
      options.onTick?.(displayedText.value)

      // 随机间隔 20~60ms（模拟人类打字节奏）
      const nextDelay = Math.floor(Math.random() * 40 + 20)
      setTimeout(tick, nextDelay)
    }

    tick()
  }

  /** 立即完成打字（跳过动画） */
  function completeTyping() {
    displayedText.value = accumulatedText.value
    cursorIdx.value = accumulatedText.value.length
    isTyping.value = false
  }

  // 当 accumulatedText 增长时自动推进打字机
  watch(accumulatedText, () => {
    if (!isTyping.value && cursorIdx.value < accumulatedText.value.length) {
      startTyping()
    }
  })

  return {
    displayedText,
    isTyping,
    typedComplete,
    startTyping,
    completeTyping,
  }
}
```

#### TypingEffect.vue（附带闪烁光标）

```vue
<!-- src/components/chat/TypingEffect.vue -->
<template>
  <div class="typing-effect">
    <MarkdownRenderer :text="displayedText" />
    <span v-if="isTyping" class="typing-cursor" aria-hidden="true">▌</span>
  </div>
</template>

<script setup lang="ts">
import { toRef } from 'vue'
import { useTyping } from '@/composables/useTyping'
import MarkdownRenderer from '@/components/markdown/MarkdownRenderer.vue'

const props = defineProps<{ streamText: string }>()
const { displayedText, isTyping, completeTyping } = useTyping(toRef(props, 'streamText'))

// 用户点击发送新的消息时，立即完成当前打字
defineExpose({ completeTyping })
</script>

<style scoped>
.typing-cursor {
  display: inline-block;
  animation: blink 0.8s step-end infinite;
  color: var(--cpq-primary, #1a56db);
  font-weight: bold;
  margin-left: 2px;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
</style>
```

### 5.2 BOM 表格虚拟滚动（物料行数 > 100）

```typescript
// src/composables/useBomTable.ts
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { BomRow } from '@/types/bom'

export function useBomTable(rows: BomRow[], options: { rowHeight?: number; overscan?: number } = {}) {
  const { rowHeight = 48, overscan = 5 } = options
  const containerRef = ref<HTMLElement | null>(null)
  const scrollTop = ref(0)
  const visibleCount = ref(20)

  const totalHeight = computed(() => rows.length * rowHeight)

  const visibleRows = computed(() => {
    const start = Math.max(0, Math.floor(scrollTop.value / rowHeight) - overscan)
    const end = Math.min(rows.length, start + visibleCount.value + overscan * 2)
    return rows.slice(start, end).map((row, i) => ({
      ...row,
      _index: start + i,
      _style: { transform: `translateY(${(start + i) * rowHeight}px)` },
    }))
  })

  function onScroll(e: Event) {
    const el = e.target as HTMLElement
    scrollTop.value = el.scrollTop
  }

  function resizeObserver(entries: ResizeObserverEntry[]) {
    const h = entries[0]?.contentRect.height || 600
    visibleCount.value = Math.ceil(h / rowHeight) + overscan * 2
  }

  let ro: ResizeObserver | null = null

  onMounted(() => {
    if (containerRef.value) {
      ro = new ResizeObserver(resizeObserver)
      ro.observe(containerRef.value)
    }
  })

  onUnmounted(() => { ro?.disconnect() })

  return { containerRef, totalHeight, visibleRows, onScroll }
}
```

```vue
<!-- CpqBomTable.vue 虚拟滚动结构 -->
<template>
  <div ref="containerRef" class="cpq-bom-table" @scroll="onScroll" style="overflow: auto; max-height: 480px;">
    <div :style="{ height: totalHeight + 'px', position: 'relative' }">
      <div v-for="row in visibleRows" :key="row._index" :style="row._style" class="bom-row">
        <!-- 行内容... -->
      </div>
    </div>
  </div>
</template>
```

### 5.3 方案对比面板的 diff 高亮算法

```typescript
// src/composables/useCompareDiff.ts
import { diffWords, diffArrays } from 'diff'
import { computed, type Ref } from 'vue'

export interface DiffSegment {
  value: string
  added?: boolean
  removed?: boolean
}

/**
 * 两个方案的逐字段 diff 比较
 * 使用 'diff' 库的 diffWords 做词级对比，返回高亮标记数组
 */
export function useCompareDiff(schemeA: Ref<string[]>, schemeB: Ref<string[]>) {
  const diffs = computed(() => {
    const a = schemeA.value
    const b = schemeB.value
    if (a.length !== b.length) {
      // 长度不同时，用数组级 diff
      return diffArrays(a, b).flatMap<DiffSegment>(part => {
        if (part.added) return part.value.map(v => ({ value: v, added: true }))
        if (part.removed) return part.value.map(v => ({ value: v, removed: true }))
        return part.value.map(v => ({ value: v }))
      })
    }
    // 字段对比
    return a.flatMap((valA, i) => {
      const valB = b[i]
      if (valA === valB) return [{ value: valA }]
      const changes = diffWords(valA, valB)
      return [{ value: `${i + 1}. `, _label: true }, ...changes] as DiffSegment[]
    })
  })

  return { diffs }
}
```

### 5.4 设置配置的实时保存与 Agent 重载

```typescript
// src/composables/useAutoSave.ts
import { watch, type Ref } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useDebounceFn } from '@vueuse/core' // 或手动 debounce

export function useAutoSave(
  settings: Ref<Record<string, unknown>>,
  options: { delay?: number; onReload?: () => Promise<void> } = {}
) {
  const { delay = 800 } = options
  const store = useSettingsStore()

  const save = useDebounceFn(async (newVal: Record<string, unknown>) => {
    try {
      await store.saveSettings(newVal)
      store.setDirty(false)
    } catch (err) {
      console.error('[AutoSave] Save failed:', err)
    }
  }, delay)

  watch(settings, (newVal) => {
    save(newVal)
    store.setDirty(true)
  }, { deep: true })

  /** 触发 Agent 热重载（不重启应用，仅重新加载配置） */
  async function reloadAgent() {
    try {
      const resp = await fetch('/api/agent/reload', { method: 'POST' })
      if (!resp.ok) throw new Error('Reload failed')
      options.onReload?.()
    } catch (err) {
      console.error('[Agent Reload] Failed:', err)
    }
  }

  return { save, reloadAgent }
}
```

---

## 6. 错误处理

### 6.1 错误场景与 UI 处理矩阵

| 错误场景 | 检测方式 | UI 处理 | 恢复策略 |
|----------|----------|---------|----------|
| **网络断开** | `fetch` 连接拒绝 / DNS 解析失败 → `TypeError: Failed to fetch` | 底部状态栏显示红色「网络断开」指示 + 顶部 ElAlert 提示 | RetryWithBackoff 自动重连，指数退避最长 30s |
| **SSE 中断** | ReadableStream 读取异常 / SSEDeliveryError | 消息气泡下方显示「接收中断，点击重新生成」按钮 | 调用 `startStream()` 重置流 |
| **Agent 超时** | SSETimeoutError (180s 无响应) | 消息气泡显示「Agent 响应超时」+ 重试/取消 | 提示用户缩短问题或简化查询条件 |
| **CPQ API 报错** | SSE event type = 'error' / HTTP 4xx/5xx | 消息中内嵌红色错误卡片 + 错误码和详情 | Agent 自动重试（可幂等的操作）或引导用户 |
| **渲染错误** | Vue 组件渲染异常 | `ErrorBoundary` 组件捕获，回退显示纯文本 | 开发环境输出 console.error 调试日志 |

### 6.2 错误 UI 状态组件

```vue
<!-- src/components/common/ErrorAlert.vue -->
<template>
  <div :class="['error-alert', `error-alert--${level}`]" role="alert" :aria-live="level === 'error' ? 'assertive' : 'polite'">
    <el-alert
      v-if="level === 'banner'"
      :title="title"
      :description="description"
      type="error"
      show-icon
      :closable="closable"
      @close="$emit('dismiss')"
    >
      <template #default>
        <p class="error-detail">{{ description }}</p>
        <div v-if="actions?.length" class="error-actions">
          <el-button v-for="act in actions" :key="act.label" size="small" @click="act.handler">
            {{ act.label }}
          </el-button>
        </div>
      </template>
    </el-alert>

    <div v-else-if="level === 'inline'" class="error-inline">
      <el-icon class="error-icon"><WarningFilled /></el-icon>
      <span class="error-text">{{ description }}</span>
      <el-button v-if="action" text size="small" @click="action.handler">{{ action.label }}</el-button>
    </div>

    <!-- 连通性指示器（底部状态栏小圆点） -->
    <div v-else-if="level === 'dot'" class="error-dot" :class="`error-dot--${status}`">
      <span class="dot" />
      <span class="dot-label">{{ statusLabel }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  level: 'banner' | 'inline' | 'dot'
  status?: 'connected' | 'connecting' | 'disconnected' | 'error'
  statusLabel?: string
  title?: string
  description?: string
  closable?: boolean
  actions?: Array<{ label: string; handler: () => void }>
  action?: { label: string; handler: () => void }
}>()

defineEmits<{ dismiss: [] }>()
</script>

<style scoped>
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.dot--connected { background: #22c55e; }
.dot--connecting { background: #eab308; animation: pulse 1s infinite; }
.dot--disconnected { background: #ef4444; }
.dot--error { background: #ef4444; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
</style>
```

### 6.3 Pinia SSE 连接状态 Store

```typescript
// src/stores/sse.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export type SSEConnectionStatus = 'idle' | 'connecting' | 'connected' | 'disconnected' | 'reconnecting'

export const useSSEStore = defineStore('sse', () => {
  const status = ref<SSEConnectionStatus>('idle')
  const retryAttempt = ref(0)
  const retryDelay = ref(0)
  const lastError = ref<string | null>(null)
  const connectedAt = ref<number | null>(null)

  const isConnected = computed(() => status.value === 'connected')

  function setConnecting() { status.value = 'connecting'; lastError.value = null }
  function setConnected() { status.value = 'connected'; connectedAt.value = Date.now(); retryAttempt.value = 0 }
  function setReconnecting(attempt: number) { status.value = 'reconnecting'; retryAttempt.value = attempt }
  function setDisconnected(reason: string) { status.value = 'disconnected'; lastError.value = reason }
  function setIdle() { /* 单次流结束后回到 idle，不代表断连 */ }
  function setRetryDelay(ms: number) { retryDelay.value = ms }

  async function reconnect() { /* 触发重连逻辑 */ }

  return { status, retryAttempt, retryDelay, lastError, connectedAt, isConnected, setConnecting, setConnected, setReconnecting, setDisconnected, setIdle, setRetryDelay, reconnect }
})
```

---

## 7. 打包部署

### 7.1 Vite 环境变量管理

```env
# .env (公共)
VITE_APP_NAME=CPQ Agent App
VITE_APP_VERSION=1.0.0

# .env.development (开发)
VITE_API_BASE_URL=http://localhost:8000
VITE_SSE_URL=http://localhost:8000
VITE_TARGET=browser

# .env.production (生产)
VITE_API_BASE_URL=__API_URL__   # 占位符，构建时替换
VITE_SSE_URL=__SSE_URL__
VITE_TARGET=electron
```

```typescript
// 使用方式：所有 API 请求通过 import.meta.env.VITE_API_BASE_URL
const API_BASE = import.meta.env.VITE_API_BASE_URL
```

### 7.2 Electron 配置 (electron/electron-builder.yml)

```yaml
# electron/electron-builder.yml
appId: com.cpq.agent-app
productName: CPQ Agent App
directories:
  output: release

files:
  - dist/**/*
  - dist-electron/**/*

win:
  target:
    - target: nsis
      arch: [x64]
  icon: public/logo.ico

mac:
  target:
    - target: dmg
      arch: [x64, arm64]
  icon: public/logo.icns
  category: public.app-category.business

linux:
  target:
    - target: AppImage
      arch: [x64]
  icon: public/logo.png

nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true
  installerIcon: public/logo.ico
```

### 7.3 Electron 主进程 (electron/main.ts)

```typescript
import { app, BrowserWindow, ipcMain } from 'electron'
import { join } from 'path'

let mainWindow: BrowserWindow | null = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 960,
    minHeight: 640,
    webPreferences: {
      preload: join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    titleBarStyle: 'hiddenInset', // macOS 更现代
  })

  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL)
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(join(__dirname, '../dist/index.html'))
  }
}

app.whenReady().then(createWindow)
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit() })
app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow() })

// IPC：配置持久化
ipcMain.handle('get-settings', () => {
  const { readFileSync, existsSync } = require('fs')
  const settingsPath = join(app.getPath('userData'), 'settings.json')
  if (existsSync(settingsPath)) {
    return JSON.parse(readFileSync(settingsPath, 'utf-8'))
  }
  return {}
})

ipcMain.handle('set-settings', (_event, settings) => {
  const { writeFileSync } = require('fs')
  const settingsPath = join(app.getPath('userData'), 'settings.json')
  writeFileSync(settingsPath, JSON.stringify(settings, null, 2))
})
```

### 7.4 Electron 预加载脚本 (electron/preload.ts)

```typescript
import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  getSettings: () => ipcRenderer.invoke('get-settings'),
  setSettings: (settings: Record<string, unknown>) => ipcRenderer.invoke('set-settings', settings),
  onMenuAction: (callback: (action: string) => void) => {
    ipcRenderer.on('menu-action', (_event, action) => callback(action))
  },
})
```

### 7.5 构建命令

```bash
# 开发
npm run dev              # 浏览器模式（本地调试 UI + SSE）
npm run electron:dev     # Electron 桌面模式

# 生产构建
npm run build            # 纯 Web 打包
npm run electron:build   # Electron 桌面安装包（输出到 release/）
```

---

## 8. PWA 配置

### 8.1 manifest.json

```json
{
  "name": "CPQ Agent App",
  "short_name": "CPQ Agent",
  "description": "AI 驱动的 CPQ 配单桌面应用",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#1a56db",
  "orientation": "any",
  "icons": [
    { "src": "/logo-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/logo-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/logo-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

### 8.2 Service Worker (VitePWA 插件自动生成 + 自定义 runtime 缓存)

VitePWA 插件使用 Workbox 自动生成 SW，我们通过 `vite.config.ts` 中的 `workbox.runtimeCaching` 配置自定义缓存策略：

```typescript
// vite.config.ts — VitePWA 插件的 workbox 配置
workbox: {
  globPatterns: ['**/*.{js,css,html,svg,png,ico,woff2}'],
  runtimeCaching: [
    // API 请求 — NetworkFirst（优先网络，网络失败时使用缓存）
    {
      urlPattern: /^https:\/\/api\.*/i,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'api-cache',
        networkTimeoutSeconds: 5,
        expiration: { maxEntries: 50, maxAgeSeconds: 60 * 60 * 24 },
      },
    },
    // 静态资源 — CacheFirst
    {
      urlPattern: /\.(?:png|jpg|jpeg|svg|gif|woff2?)$/,
      handler: 'CacheFirst',
      options: {
        cacheName: 'static-assets',
        expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 30 },
      },
    },
    // Element Plus 字体/图标
    {
      urlPattern: /^https:\/\/unpkg\.com.*element-plus.*/,
      handler: 'StaleWhileRevalidate',
      options: {
        cacheName: 'element-plus-cache',
        expiration: { maxEntries: 20, maxAgeSeconds: 60 * 60 * 24 * 7 },
      },
    },
  ],
},
```

### 8.3 离线缓存策略

| 资源类型 | 缓存策略 | 说明 |
|----------|----------|------|
| App Shell (HTML/JS/CSS) | **Precache** (globPatterns) | 应用核心文件在 SW 安装阶段预缓存 |
| API SSE 响应 | **NetworkOnly** | 不缓存流式数据，需要实时性 |
| 历史消息 | **IndexedDB** (手动) | 用户已完成的对话存到浏览器 IndexedDB |
| 设置配置 | **localStorage / Electron userData** | 用户偏好设置持久化 |
| Element Plus 图标 | **CacheFirst** | 不常变化的第三方资源 |
| 产品图片 | **StaleWhileRevalidate** | 先展示缓存版本，后台更新 |

### 8.4 手动 ImageDB 存储（历史消息持久化）

```typescript
// src/services/db.ts — IndexedDB 封装（非 PWA SW，是应用内持久化）
const DB_NAME = 'cpq-agent-db'
const DB_VERSION = 1

export function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION)
    req.onupgradeneeded = () => {
      const db = req.result
      if (!db.objectStoreNames.contains('sessions')) {
        db.createObjectStore('sessions', { keyPath: 'id' })
      }
      if (!db.objectStoreNames.contains('messages')) {
        const store = db.createObjectStore('messages', { keyPath: 'id' })
        store.createIndex('sessionId', 'sessionId', { unique: false })
      }
    }
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

export async function saveMessage(message: { id: string; sessionId: string; content: string; role: 'user' | 'assistant'; timestamp: number }) {
  const db = await openDB()
  const tx = db.transaction('messages', 'readwrite')
  tx.objectStore('messages').put(message)
  return new Promise<void>((resolve, reject) => {
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}
```

---

## 附录：关键文件索引

| 文件路径 | 作用 |
|----------|------|
| `src/services/sse.ts` | SSE 流式通信核心（fetch + ReadableStream） |
| `src/services/retry.ts` | 指数退避断线重连 |
| `src/composables/useSse.ts` | SSE 连接管理组合式函数 |
| `src/composables/useTyping.ts` | 打字机流式效果（含 Markdown token 检测） |
| `src/utils/markdown.ts` | markdown-it 渲染器配置 |
| `src/utils/markdown-rules.ts` | 自定义渲染规则（product-card / bom-table / compare-panel） |
| `src/components/markdown/MarkdownRenderer.vue` | Markdown 渲染 + 自定义组件挂载桥接 |
| `src/composables/useBomTable.ts` | BOM 表格虚拟滚动 |
| `src/composables/useCompareDiff.ts` | 方案对比 diff 高亮 |
| `src/composables/useAutoSave.ts` | 设置实时保存 + Agent 重载 |
| `src/stores/sse.ts` | SSE 连接状态 Pinia store |
| `src/router/guards.ts` | 路由守卫（标题、连接检查、脏状态提醒） |
| `vite.config.ts` | Vite 配置（多目标构建、PWA、Electron） |
| `electron/main.ts` | Electron 主进程 |
| `electron/electron-builder.yml` | 桌面安装包构建配置 |
| `sw.ts` | PWA Service Worker |

---

> **文档版本**：v1.0
> **最后更新**：2026-07-05
> **技术栈**：Vue 3 + Composition API + TypeScript + Element Plus + Pinia + markdown-it + Fetch SSE
> **桌面打包**：Electron (可选) + electron-builder
> **PWA 支持**：vite-plugin-pwa + Workbox
