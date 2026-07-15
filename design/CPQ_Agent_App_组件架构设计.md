# CPQ Agent App - 前端组件架构设计文档

> **版本**: v1.0
> **作者**: 全栈精品UI工程师
> **日期**: 2026-07-05
> **目标交付**: 前端开发专家实现参考

---

## 目录

1. [技术栈概览](#1-技术栈概览)
2. [项目目录结构](#2-项目目录结构)
3. [组件树设计](#3-组件树设计)
4. [核心组件接口定义](#4-核心组件接口定义)
5. [Pinia Store 状态管理方案](#5-pinia-store-状态管理方案)
6. [SSE 流式数据驱动方案](#6-sse-流式数据驱动方案)
7. [跨平台适配方案](#7-跨平台适配方案)
8. [性能优化方案](#8-性能优化方案)
9. [关键技术难点实现方案](#9-关键技术难点实现方案)

---

## 1. 技术栈概览

| 层级 | 技术选型 | 选型理由 |
|------|----------|----------|
| **框架** | Vue 3.4+ (Composition API) | 响应式系统 + TypeScript 深度集成 |
| **构建工具** | Vite 5+ | 极速 HMR，Electron 兼容 |
| **语言** | TypeScript 5+ (strict mode) | 全量类型安全 |
| **状态管理** | Pinia 2+ | Vue 3 官方推荐，模块化设计 |
| **UI 组件库** | Element Plus 2.7+ | 与 CPQ Portal 一致，A11y 友好 |
| **CSS 方案** | UnoCSS (Atomic CSS) + CSS Modules | 零运行时 + 按需生成 |
| **网络层** | ofetch (native fetch wrapper) | 轻量，SSE 原生支持 |
| **桌面壳** | Electron 30+ | 跨平台原生体验 |
| **表格** | @tanstack/vue-table (headless) | DOM 虚拟化 + 列控制 |
| **虚拟滚动** | @tanstack/vue-virtual | 10000+ 消息流畅滚动 |
| **图表** | ECharts 5 | BOM 可视化、价格曲线 |
| **Markdown** | marked | 轻量快速，流式兼容 |
| **国际化** | vue-i18n 9 | 预留多语言扩展 |
| **持久化** | pinia-plugin-persistedstate | Store 状态持久化 |
| **测试** | Vitest + Vue Test Utils + Playwright | 单测 + E2E |

---

## 2. 项目目录结构

```
cpq-agent-app/
├── electron/                    # Electron 主进程
│   ├── main.ts
│   ├── preload.ts
│   └── updater.ts
├── src/
│   ├── app/                     # App 级组装层
│   │   ├── App.vue              # 根组件
│   │   ├── layouts/             # 布局系统
│   │   │   ├── AppShell.vue         # App 壳 (标题栏+侧边栏+内容区)
│   │   │   ├── TitleBar.vue         # 自定义标题栏
│   │   │   ├── Sidebar.vue          # 侧边导航栏
│   │   │   └── ResponsiveContainer.vue  # 响应式容器
│   │   └── providers/           # Provide/Inject 上下文
│   │       ├── ThemeProvider.vue
│   │       └── I18nProvider.vue
│   │
│   ├── features/                # 领域功能模块
│   │   ├── chat/                # 对话模块
│   │   │   ├── components/
│   │   │   │   ├── ChatView.vue
│   │   │   │   ├── MessageList.vue
│   │   │   │   ├── MessageItem.vue
│   │   │   │   ├── MessageBubble.vue
│   │   │   │   ├── StreamingText.vue
│   │   │   │   ├── ThinkingChain.vue
│   │   │   │   ├── TypingIndicator.vue
│   │   │   │   ├── ChatInput.vue
│   │   │   │   ├── ContextChips.vue
│   │   │   │   └── QuickActions.vue
│   │   │   ├── composables/
│   │   │   │   ├── useChat.ts
│   │   │   │   ├── useSSE.ts
│   │   │   │   └── useStreamingRender.ts
│   │   │   ├── stores/
│   │   │   │   ├── chatStore.ts
│   │   │   │   └── streamingStore.ts
│   │   │   └── types/
│   │   │       └── message.ts
│   │   │
│   │   ├── product-recommendation/  # 产品推荐模块
│   │   │   ├── components/
│   │   │   │   ├── ProductCard.vue
│   │   │   │   ├── ProductCardSkeleton.vue
│   │   │   │   ├── ProductGrid.vue
│   │   │   │   ├── MatchingBadge.vue
│   │   │   │   └── ProductDetailDrawer.vue
│   │   │   └── types/
│   │   │       └── product.ts
│   │   │
│   │   ├── bom/                    # BOM 清单模块
│   │   │   ├── components/
│   │   │   │   ├── BomTable.vue
│   │   │   │   ├── BomSummary.vue
│   │   │   │   ├── BomCostChart.vue
│   │   │   │   └── BomExportMenu.vue
│   │   │   ├── composables/
│   │   │   │   ├── useBomTable.ts
│   │   │   │   └── useBomWorker.ts
│   │   │   └── stores/
│   │   │       └── bomStore.ts
│   │   │
│   │   ├── comparison/             # 方案对比模块
│   │   │   └── components/
│   │   │       ├── ComparisonPanel.vue
│   │   │       ├── ComparisonColumn.vue
│   │   │       ├── ComparisonRow.vue
│   │   │       ├── ComparisonDiff.vue
│   │   │       └── ComparisonSummary.vue
│   │   │
│   │   ├── quote/                  # 报价模块
│   │   │   ├── components/
│   │   │   │   ├── QuoteCard.vue
│   │   │   │   ├── QuotePreview.vue
│   │   │   │   ├── GenerateQuoteBtn.vue
│   │   │   │   └── QuoteHistory.vue
│   │   │   └── stores/
│   │   │       └── quoteStore.ts
│   │   │
│   │   └── settings/               # 设置模块
│   │       ├── components/
│   │       │   ├── SettingsPanel.vue
│   │       │   ├── SettingsTabs.vue
│   │       │   ├── SettingsSection.vue
│   │       │   └── settings-items/
│   │       │       ├── ModelSelector.vue
│   │       │       ├── ThemeToggle.vue
│   │       │       ├── LanguageSelector.vue
│   │       │       ├── ApiKeyInput.vue
│   │       │       └── ShortcutConfig.vue
│   │       └── stores/
│   │           └── settingsStore.ts
│   │
│   ├── shared/                 # 共享层
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   │   ├── AppIcon.vue
│   │   │   │   ├── AppButton.vue
│   │   │   │   ├── AppBadge.vue
│   │   │   │   ├── GlassPanel.vue
│   │   │   │   └── SkeletonLoader.vue
│   │   │   ├── feedback/
│   │   │   │   ├── ToastNotification.vue
│   │   │   │   ├── ErrorBoundary.vue
│   │   │   │   └── EmptyState.vue
│   │   │   └── data-display/
│   │   │       ├── VirtualList.vue
│   │   │       ├── DataTable.vue
│   │   │       └── ProgressIndicator.vue
│   │   ├── composables/
│   │   │   ├── useBreakpoint.ts
│   │   │   ├── useKeyboard.ts
│   │   │   ├── useDebounce.ts
│   │   │   ├── useThrottle.ts
│   │   │   └── useTheme.ts
│   │   ├── stores/
│   │   │   ├── appStore.ts
│   │   │   └── uiStore.ts
│   │   ├── utils/
│   │   │   ├── format.ts
│   │   │   ├── validator.ts
│   │   │   └── platform.ts
│   │   └── constants/
│   │       └── eventBus.ts
│   │
│   ├── workers/                # Web Workers
│   │   └── bom.worker.ts
│   │
│   └── types/                  # 全局类型
│       ├── api.ts
│       ├── global.d.ts
│       └── env.d.ts
│
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── uno.config.ts
└── electron-builder.yml
```

---

## 3. 组件树设计

### 3.1 完整组件树 ASCII 图

```
App.vue
│
├─ <ThemeProvider>                              # 主题上下文注入
│  └─ <I18nProvider>                            # 国际化上下文注入
│     └─ <AppShell>                             # 应用壳层
│        │
│        ├─ <TitleBar>                          # 自定义标题栏
│        │  ├─ platform="darwin|win32"
│        │  ├─ @minimize / @maximize / @close
│        │  └─ <AppIcon> (macOS 居中图标)
│        │
│        ├─ <Sidebar>                           # 侧边导航
│        │  ├─ <nav-item icon slot>
│        │  │  ├─ "对话"
│        │  │  ├─ "BOM 清单"
│        │  │  ├─ "方案对比"
│        │  │  ├─ "报价管理"
│        │  │  └─ "设置"
│        │  └─ <user-avatar slot="footer">
│        │
│        └─ <ResponsiveContainer>               # 内容区（响应式断点驱动）
│           │  ┌──────────────────────────────┐
│           │  │  根据活跃视图动态渲染:        │
│           │  │                              │
│           │  │  <ChatView> ──────────────── │ 【主视图】
│           │  │  ├─ <ContextChips>            │
│           │  │  │  └─ <el-tag>[]            │
│           │  │  ├─ <MessageList>            │ 虚拟滚动容器
│           │  │  │  └─ <MessageItem>[]       │
│           │  │  │     ├─ <MessageBubble>    │
│           │  │  │     │  ├─ <ThinkingChain> │ (仅 AI 消息)
│           │  │  │     │  ├─ <StreamingText> │ (打字机效果)
│           │  │  │     │  └─ <slot name="widget">  ← 消息类型分发
│           │  │  │     │     ├─ 产品推荐 → <ProductGrid>
│           │  │  │     │     ├─ BOM清单  → <BomTable>
│           │  │  │     │     ├─ 方案对比 → <ComparisonPanel>
│           │  │  │     │     └─ 报价确认 → <QuoteCard>
│           │  │  │     └─ <TypingIndicator>  (AI 思考中)
│           │  │  ├─ <QuickActions>           │
│           │  │  │  ├─ "配一套方案"
│           │  │  │  ├─ "生成 BOM"
│           │  │  │  ├─ "对比方案"
│           │  │  │  └─ "生成报价"
│           │  │  └─ <ChatInput>              │
│           │  │     ├─ textarea              │
│           │  │     ├─ file-upload btn       │
│           │  │     └─ send / stop btn       │
│           │  │                              │
│           │  │  <BomView/> ─────────────── │ (全屏表格)
│           │  │  <ComparisonView/> ──────── │
│           │  │  <QuoteView/> ───────────── │
│           │  │  <SettingsPanel/> ───────── │
│           │  └──────────────────────────────┘
│           │
│           └─ (叠加层/抽屉)
│              ├─ <ProductDetailDrawer>
│              └─ <SettingsPanel> (overlay 模式移动端)
```

### 3.2 组件分层原则

```
Layer 4: Pages (路由级视图)     ← ChatView, BomView, ComparisonView
Layer 3: Features (功能组件)     ← ProductCard, BomTable, QuoteCard
Layer 2: Shared (共享组件)       ← VirtualList, GlassPanel, ErrorBoundary
Layer 1: App (壳层 + 提供者)     ← AppShell, ThemeProvider, TitleBar
Layer 0: UI Atoms (Element Plus)  ← el-button, el-table, el-dialog
```

**核心原则**:
- Layer 0-2 无业务耦合，可独立测试
- Layer 3 组件通过 Props 接收数据，通过 Emits 上报事件，不直接操作 Store
- Layer 4 作为容器，连接 Store + Composables + Feature 组件

---

## 4. 核心组件接口定义

### 4.1 MessageList — 消息列表（虚拟滚动）

```typescript
// ==============================
// MessageList.vue
// ==============================

interface MessageListProps {
  /** 消息数组 */
  messages: ChatMessage[]
  /** 是否正在加载历史消息 */
  isLoadingHistory?: boolean
  /** 是否自动滚动到底部 */
  autoScroll?: boolean
  /** 虚拟滚动阈值（超过此数量启用） */
  virtualThreshold?: number  // default: 50
  /** 预估每项高度 */
  estimatedItemHeight?: number  // default: 120
}

interface MessageListEmits {
  (e: 'load-more'): void
  (e: 'retry-message', messageId: string): void
  (e: 'scroll-position', position: { scrollTop: number; isAtBottom: boolean }): void
}
```

### 4.2 MessageItem — 单条消息路由

```typescript
// ==============================
// MessageItem.vue
// ==============================

interface MessageItemProps {
  message: ChatMessage
  showTimestamp?: boolean
  isGrouped?: boolean  // 同作者连续消息
}

interface MessageItemEmits {
  (e: 'action', payload: { action: string; messageId: string; data?: any }): void
  (e: 'retry', messageId: string): void
}

// 内部根据 message.widget.type 动态渲染 Feature 组件：
// - 'thinking'  → ThinkingChain
// - 'text'      → StreamingText
// - 'product'   → ProductGrid
// - 'bom'       → BomTable
// - 'comparison'→ ComparisonPanel
// - 'quote'     → QuoteCard
// - 'error'     → ErrorState
```

### 4.3 StreamingText — 流式打字机

```typescript
// ==============================
// StreamingText.vue
// ==============================

interface StreamingTextProps {
  /** 原始文本内容 */
  content: string
  /** 已渲染到的字符索引 */
  renderedIndex?: number
  /** 打字速度 (ms/字符) */
  speed?: number           // default: 15
  /** 是否启用 Markdown 渲染 */
  enableMarkdown?: boolean  // default: true
  /** 是否正在流式传输中 */
  isStreaming?: boolean
  /** 是否显示光标闪烁 */
  showCursor?: boolean     // default: true
}

interface StreamingTextEmits {
  (e: 'typing-complete'): void
  (e: 'progress', percent: number): void
}
```

### 4.4 ThinkingChain — 思考过程

```typescript
// ==============================
// ThinkingChain.vue
// ==============================

interface ThinkingChainProps {
  steps: ThinkingStep[]
  defaultExpanded?: boolean  // default: true (流式时) / false (完成后)
  isThinking?: boolean
}

interface ThinkingStep {
  id: string
  title: string              // e.g. "分析产品需求...", "匹配 SKU..."
  status: 'pending' | 'running' | 'completed' | 'error'
  description?: string
  duration?: number          // 耗时(ms)
}

interface ThinkingChainEmits {
  (e: 'toggle', expanded: boolean): void
}
```

### 4.5 ProductCard — 产品推荐卡片

```typescript
// ==============================
// ProductCard.vue
// ==============================

interface ProductCardProps {
  product: RecommendedProduct
  rank?: number
  selected?: boolean
  mode?: 'compact' | 'detail'  // default: 'compact'
}

interface RecommendProduct {
  id: string
  sku: string
  name: string
  image: string
  category: string
  specSummary: Array<{ label: string; value: string; unit?: string }>
  unitPrice: number
  currency: string
  matchScore: number       // 0-100
  matchReasons: string[]
  inStock: boolean
  leadTime: number         // 天
}

interface ProductCardEmits {
  (e: 'select', productId: string): void
  (e: 'detail', productId: string): void
  (e: 'add-to-bom', productId: string): void
  (e: 'compare', productId: string): void
}

interface ProductCardSlots {
  price?: (props: { price: number; currency: string }) => any
  actions?: (props: { product: RecommendProduct }) => any
}
```

### 4.6 BomTable — BOM 清单表格

```typescript
// ==============================
// BomTable.vue
// ==============================

interface BomTableProps {
  items: BomItem[]
  columns?: BomColumnDef[]
  groupBy?: 'category' | 'supplier' | 'none'
  editable?: boolean
  showSummary?: boolean
  maxHeight?: number | string
}

interface BomItem {
  id: string
  lineNo: number
  sku: string
  name: string
  category: string
  spec: Record<string, string>
  quantity: number
  unit: string
  unitPrice: number
  totalPrice: number
  supplier: string
  leadTime: number
  notes?: string
  children?: BomItem[]     // 可展开子项
}

interface BomColumnDef {
  key: string
  label: string
  sortable?: boolean
  filterable?: boolean
  width?: number
  align?: 'left' | 'center' | 'right'
  format?: 'currency' | 'number' | 'percent' | 'date'
  hidden?: boolean
}

interface BomTableEmits {
  (e: 'row-expand', item: BomItem, expanded: boolean): void
  (e: 'sort', sortBy: { key: string; order: 'asc' | 'desc' }): void
  (e: 'quantity-change', itemId: string, quantity: number): void
  (e: 'export', format: 'xlsx' | 'csv' | 'pdf'): void
  (e: 'remove-item', itemId: string): void
}
```

### 4.7 ComparisonPanel — 方案对比面板

```typescript
// ==============================
// ComparisonPanel.vue
// ==============================

interface ComparisonPanelProps {
  solutions: Solution[]
  dimensions: ComparisonDimension[]
  highlightDiff?: boolean  // default: true
}

interface Solution {
  id: string
  name: string
  values: Record<string, string | number | string[] | null>
  summary: {
    totalCost: number
    totalItems: number
    leadTime: number
    pros: string[]
    cons: string[]
  }
}

interface ComparisonDimension {
  key: string
  label: string
  type: 'text' | 'currency' | 'number' | 'list' | 'rating'
  unit?: string
  better?: 'higher' | 'lower'
}

interface ComparisonPanelEmits {
  (e: 'select', solutionId: string): void
  (e: 'close'): void
}
```

### 4.8 QuoteCard — 报价确认卡片

```typescript
// ==============================
// QuoteCard.vue
// ==============================

interface QuoteCardProps {
  quote: QuoteData
  editable?: boolean
  isGenerating?: boolean
  status?: 'draft' | 'pending' | 'confirmed' | 'expired'
}

interface QuoteData {
  id: string
  items: Array<{ sku: string; name: string; quantity: number; unitPrice: number; total: number }>
  subtotal: number
  tax: number
  discount: number
  total: number
  currency: string
  validUntil: string
  terms: string
  notes?: string
}

interface QuoteCardEmits {
  (e: 'edit'): void
  (e: 'confirm', quoteId: string): void
  (e: 'generate', quoteId: string): void
  (e: 'reject', quoteId: string): void
}
```

### 4.9 ChatInput — 输入区域

```typescript
// ==============================
// ChatInput.vue
// ==============================

interface ChatInputProps {
  placeholder?: string
  disabled?: boolean
  maxLength?: number          // default: 4000
  isSending?: boolean
  enableFileUpload?: boolean  // default: true
  acceptFileTypes?: string[]  // default: ['.pdf', '.xlsx', '.csv', '.png', '.jpg']
}

interface ChatInputEmits {
  (e: 'send', payload: { text: string; files?: File[] }): void
  (e: 'stop-generation'): void
  (e: 'input-change', text: string): void
}
```

---

## 5. Pinia Store 状态管理方案

### 5.1 状态分类原则

```
┌─────────────────────────────────────────────────┐
│              状态管理决策树                       │
├─────────────────────────────────────────────────┤
│                                                  │
│  Q: 这个状态需要跨多个组件共享吗？                 │
│     ├─ YES → Pinia Store                         │
│     └─ NO  → 组件内部 ref/reactive               │
│                                                  │
│  Q: 这个状态需要持久化吗？（刷新保留）              │
│     ├─ YES → Pinia + localStorage/pinia-plugin   │
│     └─ NO  → Pinia（不持久化）或组件内部          │
│                                                  │
│  Q: 这个状态是否需要中间件（日志/撤销/同步）？      │
│     ├─ YES → Pinia Store                         │
│     └─ NO  → 组件 Composables                    │
│                                                  │
└─────────────────────────────────────────────────┘
```

### 5.2 Store 架构全景

```
                    ┌──────────────┐
                    │   appStore   │  ← 全局根 Store
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
  ┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
  │   uiStore    │ │ settingsStore│ │  themeStore │
  │ (UI 状态)    │ │ (持久化)     │ │ (主题配置)  │
  └──────────────┘ └─────────────┘ └─────────────┘
          │
          │ (共享层)
          │
  ┌───────┴──────────────────────────────────────┐
  │              Feature Stores                   │
  │                                               │
  │  ┌───────────┐ ┌──────────┐ ┌─────────────┐ │
  │  │ chatStore │ │ bomStore │ │ quoteStore  │ │
  │  │ (对话)    │ │ (BOM)    │ │ (报价)      │ │
  │  └─────┬─────┘ └──────────┘ └─────────────┘ │
  │        │                                      │
  │  ┌─────▼────────┐                            │
  │  │streamingStore│                            │
  │  │ (流式传输)   │                            │
  │  └──────────────┘                            │
  └──────────────────────────────────────────────┘
```

### 5.3 各 Store 详细设计

#### 5.3.1 appStore — 全局应用状态

```typescript
// stores/appStore.ts
interface AppState {
  initialized: boolean
  platform: 'darwin' | 'win32' | 'linux' | 'web'
  windowState: {
    isMaximized: boolean
    isFullscreen: boolean
    width: number
    height: number
  }
  onlineStatus: 'online' | 'offline'
  connectionStatus: 'connected' | 'connecting' | 'disconnected' | 'error'
  activeSessionId: string | null
  sessions: Array<{ id: string; title: string; createdAt: string; messageCount: number }>
}

// Actions:
// - initialize()       : 应用启动初始化
// - setWindowState()   : 更新窗口状态
// - switchSession()    : 切换活跃会话
// - createSession()    : 创建新会话
// - deleteSession()    : 删除会话
```

#### 5.3.2 uiStore — UI 交互状态（不持久化）

```typescript
// stores/uiStore.ts
interface UIState {
  sidebar: {
    collapsed: boolean
    width: number
  }
  activePanels: Set<'settings' | 'product-detail' | 'comparison'>
  notifications: Array<{ id: string; type: 'info' | 'success' | 'warning' | 'error'; message: string }>
  globalLoading: boolean
  breakpoint: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
}
```

#### 5.3.3 chatStore — 对话状态（核心）

```typescript
// stores/chatStore.ts
interface ChatState {
  messages: Map<string, ChatMessage>
  messageIds: string[]              // 有序索引（用于虚拟滚动）
  draft: string
  isGenerating: boolean
  currentReplyId: string | null
  error: { code: string; message: string } | null
}

// 核心 Actions:
// - sendMessage(text, files?)  : 发送消息
// - stopGeneration()            : 停止生成
// - appendStreamingToken(token) : 追加流式 token
// - completeStreaming()         : 完成流式回复
// - loadHistory(sessionId)      : 加载历史消息
// - clearMessages()             : 清空对话

// Getters:
// - lastMessage
// - currentReply
// - visibleMessages(start, end)  : 虚拟列表切片
```

#### 5.3.4 streamingStore — 流式传输状态

```typescript
// stores/streamingStore.ts
interface StreamingState {
  status: 'idle' | 'connecting' | 'streaming' | 'paused' | 'error'
  thinkingSteps: ThinkingStep[]
  textBuffer: string
  totalTokens: number
  partialWidgets: Array<{ widgetId: string; type: string; data: any }>
  retryCount: number
  lastHeartbeat: number
}

// Actions:
// - startStreaming(sessionId, message)  : 发起 SSE 连接
// - handleChunk(chunk: SSEChunk)        : 处理流式数据块
// - pauseStreaming()                    : 暂停
// - resumeStreaming()                   : 恢复
// - abortStreaming()                    : 中止
// - scheduleReconnect()                 : 指数退避重连
```

#### 5.3.5 settingsStore — 设置（持久化）

```typescript
// stores/settingsStore.ts（18 个配置项，5 个分类）

interface SettingsState {
  // 1. AI 模型 (4 项)
  model: {
    provider: 'openai' | 'anthropic' | 'azure' | 'custom'
    modelName: string
    temperature: number       // 0-2
    maxTokens: number
    systemPrompt: string      // 自定义系统提示词
  }

  // 2. 界面外观 (5 项)
  appearance: {
    theme: 'light' | 'dark' | 'system'
    fontSize: 'small' | 'medium' | 'large'
    language: 'zh-CN' | 'en-US'
    messageDensity: 'compact' | 'comfortable'
    reduceMotion: boolean
  }

  // 3. 对话行为 (4 项)
  chat: {
    streamingSpeed: number    // 1-5
    showThinkingChain: boolean
    autoCollapseThinking: boolean
    contextWindow: number     // 保留最近 N 轮对话
  }

  // 4. BOM & 报价 (3 项)
  bom: {
    defaultCurrency: string
    showCostChart: boolean
    decimalPlaces: number
  }

  // 5. 快捷键 (2 项)
  shortcuts: Record<string, string>
}

// 使用 pinia-plugin-persistedstate 持久化到 localStorage
```

#### 5.3.6 组件内部状态 vs Pinia State 对照表

| 状态类型 | 示例 | 存放位置 | 理由 |
|----------|------|----------|------|
| 输入框文本 | `draftText` | chatStore | 跨组件同步 + 草稿持久化 |
| 消息列表 | `messages` | chatStore | 全局核心数据 |
| 折叠/展开状态 | `thinkingExpanded` | 组件 ref | 纯 UI 状态，仅 ThinkingChain 关心 |
| 鼠标悬停索引 | `hoveredMessageId` | 组件 ref | 仅 MessageItem 内部 |
| 拖拽尺寸 | `sidebarWidth` | uiStore | 多组件需要感知 |
| 虚拟滚动偏移 | `scrollOffset` | composable 内部 | 组件独立逻辑 |
| 表单校验状态 | `formErrors` | 组件 ref | 局部生命周期 |
| 网络重连计数 | `retryCount` | streamingStore | 跨组件协调 |

---

## 6. SSE 流式数据驱动方案

### 6.1 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                    SSE 数据流架构                             │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Backend API                                                  │
│     │                                                         │
│     │  POST /api/chat/send          → 返回 sessionId          │
│     │  GET  /api/chat/stream/:id    → SSE 长连接              │
│     │                                                         │
│  ┌──▼──────────────┐     ┌──────────────────────────┐        │
│  │  SSE Client      │────▶│  Message Parser          │        │
│  │  (useSSE)        │     │  (事件类型路由)           │        │
│  │  - 连接管理      │     └────────┬─────────────────┘        │
│  │  - 心跳检测      │              │                          │
│  │  - 自动重连      │     ┌────────▼─────────────────┐        │
│  │  - 指数退避      │     │  Chunk Dispatcher        │        │
│  └─────────────────┘     └────────┬─────────────────┘        │
│                                   │                           │
│              ┌────────────────────┼────────────────┐         │
│              │                    │                │         │
│        ┌─────▼────┐        ┌─────▼────┐    ┌─────▼────┐    │
│        │ Thinking │        │  Text    │    │  Widget  │    │
│        │ Handler  │        │  Handler │    │  Handler │    │
│        └─────┬────┘        └─────┬────┘    └─────┬────┘    │
│              │                    │                │         │
│        ┌─────▼────────────────────▼────────────────▼─────┐  │
│        │              RAF Batcher                         │  │
│        │      (requestAnimationFrame 批量刷新)            │  │
│        └────────────────────┬────────────────────────────┘  │
│                             │                               │
│        ┌────────────────────▼────────────────────────────┐  │
│        │            Pinia Store (响应式更新)              │  │
│        │      streamingStore → chatStore → 组件渲染        │  │
│        └────────────────────┬────────────────────────────┘  │
│                             │                               │
│        ┌────────────────────▼────────────────────────────┐  │
│        │           Vue Reactive Render (60fps)            │  │
│        └─────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### 6.2 SSE 协议设计

```typescript
// ==============================
// SSE 事件类型规范
// ==============================

// 服务端推送格式：
// event: <type>
// data: <json>

type SSEEventType =
  // 生命周期
  | 'stream.started'
  | 'stream.completed'
  | 'stream.error'
  // 思考过程
  | 'thinking.start'
  | 'thinking.step'
  | 'thinking.completed'
  // 文本内容
  | 'text.delta'
  | 'text.completed'
  // 结构化 Widget
  | 'widget.product_list'
  | 'widget.bom'
  | 'widget.comparison'
  | 'widget.quote'
  // 心跳
  | 'heartbeat'
```

**完整 SSE 事件序列示例**（用户: "帮我配一套数据中心制冷方案，预算50万以内"）：

```
event: stream.started
data: {"messageId":"msg_001","sessionId":"sess_42"}

event: thinking.start
data: {"messageId":"msg_001"}

event: thinking.step
data:
{"stepId":"s1","title":"解析需求：数据中心制冷，预算50万","status":"running"}

event: thinking.step
data: {"stepId":"s1","status":"completed"}

event: thinking.step
data: {"stepId":"s2","title":"匹配制冷产品 SKU...","status":"running"}

event: text.delta
data: {"messageId":"msg_001","content":"根据","index":0}

event: text.delta
data: {"messageId":"msg_001","content":"您的需求，","index":2}

// ... 继续文本增量 ...

event: thinking.step
data: {"stepId":"s2","status":"completed"}

event: thinking.completed
data: {"messageId":"msg_001","totalSteps":2,"totalDuration":3200}

event: widget.product_list
data: {"messageId":"msg_001","widgetId":"w1","action":"create","data":{"items":[]}}

event: widget.product_list
data: {"messageId":"msg_001","widgetId":"w1","action":"update","data":{"items":[{"id":"AC-8000","name":"精密空调 AC-8000"}]}}

event: widget.product_list
data: {"messageId":"msg_001","widgetId":"w1","action":"complete","data":{"items":[...3个完整产品]}}

event: text.delta
data: {"messageId":"msg_001","content":"以上是我推荐的3款产品...","index":150}

event: stream.completed
data: {"messageId":"msg_001","totalTokens":4520,"duration":6800}
```

### 6.3 useSSE Composable 核心实现

```typescript
// composables/useSSE.ts

export function useSSE(options: SSEOptions) {
  const streaming = useStreamingStore()
  const chat = useChatStore()

  const eventSource = ref<EventSource | null>(null)
  const retryCount = ref(0)
  let textBuffer = ''
  let rafId: number | null = null

  // RAF 批处理：将多个 token 合并为一帧更新
  function flushTextBuffer() {
    if (textBuffer.length === 0) return
    chat.appendStreamingToken(textBuffer)
    textBuffer = ''
    rafId = null
  }

  function scheduleFlush() {
    if (rafId === null) rafId = requestAnimationFrame(flushTextBuffer)
  }

  function connect(sessionId: string, signal?: AbortSignal) {
    streaming.setStatus('connecting')
    const es = new EventSource(`/api/chat/stream/${sessionId}`)

    es.onmessage = (event) => {
      const chunk = JSON.parse(event.data)
      dispatchChunk(chunk)
    }

    es.addEventListener('heartbeat', resetHeartbeat)
    es.addEventListener('stream.started', () => { streaming.setStatus('streaming') })
    es.addEventListener('stream.completed', teardown)
    es.onerror = () => { streaming.setStatus('error'); scheduleReconnect(sessionId) }

    if (signal) signal.addEventListener('abort', teardown)

    eventSource.value = es
    onUnmounted(teardown)
  }

  function dispatchChunk(chunk: SSEChunk) {
    switch (chunk.type) {
      case 'thinking.step':
        streaming.handleThinkingChunk(chunk)
        break
      case 'text.delta':
        textBuffer += chunk.content
        scheduleFlush()
        break
      case 'widget.product_list':
      case 'widget.bom':
      case 'widget.comparison':
      case 'widget.quote':
        streaming.handleWidgetChunk(chunk)
        break
      case 'stream.error':
        chat.appendErrorMessage(chunk.error)
        break
    }
  }

  // 指数退避重连
  function scheduleReconnect(sessionId: string) {
    if (retryCount.value >= (options.maxRetries ?? 5)) {
      chat.appendErrorMessage({ code: 'SSE_MAX_RETRIES', message: '连接失败' })
      return
    }
    const delay = Math.min(1000 * Math.pow(2, retryCount.value), 30000)
    const jitter = delay * (0.8 + Math.random() * 0.4) // ±20% 抖动
    retryCount.value++
    setTimeout(() => connect(sessionId), jitter)
  }

  return { connect, abort: teardown }
}
```

### 6.4 错误处理矩阵

| 错误类型 | 检测方式 | 处理策略 | UI 反馈 |
|----------|----------|----------|---------|
| **网络断开** | `EventSource.onerror` + `navigator.onLine` | 自动重连（指数退避） | Toast "网络已断开，正在重连..." |
| **服务端 5xx** | HTTP 状态码探测 | 指数退避重连（最多 5 次） | 错误气泡 "生成失败，点击重试" |
| **认证过期** | 401 响应 | 停止重连 → 弹出登录 | 全局 Modal |
| **心跳超时** | 45s 无 heartbeat | 主动断开 + 重连 | 静默重连（无 UI 抖动） |
| **JSON 解析错误** | `JSON.parse` 异常 | 丢弃该 chunk | 静默丢弃（console.error 日志） |
| **流式中断** | `stream.error` 事件 | 保留已生成内容 + 显示错误 | 文本保留 + [生成中断] 标记 |
| **浏览器不支持 SSE** | 特性检测 | 降级为轮询 (polling) | 静默降级 |

---

## 7. 跨平台适配方案

### 7.1 平台检测

```typescript
// utils/platform.ts
export const PLATFORM = {
  isElectron: !!(window as any).__ELECTRON__,
  isMacOS: /Mac/.test(navigator.platform),
  isWindows: /Win/.test(navigator.platform),
  isPWA: matchMedia('(display-mode: standalone)').matches,
}
```

### 7.2 响应式断点系统

```typescript
// composables/useBreakpoint.ts
type Breakpoint = 'xs' | 'sm' | 'md' | 'lg' | 'xl'

const BREAKPOINT_MAP = {
  'xs': { min: 0,    max: 639 },
  'sm': { min: 640,  max: 899 },
  'md': { min: 900,  max: 1199 },
  'lg': { min: 1200, max: 1599 },
  'xl': { min: 1600, max: Infinity }
}
```

### 7.3 布局响应策略

```
窗口宽度 → 布局自适应矩阵：

┌──────────┬──────────┬──────────┬──────────┬──────────┐
│          │   xs     │   sm     │   md     │   lg/xl  │
├──────────┼──────────┼──────────┼──────────┼──────────┤
│ Sidebar  │ 隐藏     │ 覆盖抽屉 │ 图标 64px│ 展开 240px│
│ TitleBar │ 原生(PWA)│ 原生(PWA)│ 自定义   │ 自定义   │
│ Chat     │ 全屏     │ 全屏     │ +侧面板  │ +固定面板│
│ 对比面板 │ 全屏覆盖 │ 全屏覆盖 │ 侧边抽屉 │ 并排显示 │
│ BOM 表格 │ 堆叠关键列│ 可滚动   │ 全列     │ 全列+图表│
│ 产品卡片 │ 1列      │ 2列      │ 3列      │ 4列      │
└──────────┴──────────┴──────────┴──────────┴──────────┘
```

### 7.4 Electron 特定适配

```typescript
// preload.ts - IPC 桥接
contextBridge.exposeInMainWorld('__ELECTRON__', {
  platform: process.platform,
  window: {
    onResize: (cb: Function) => ipcRenderer.on('window-resize', (_, s) => cb(s)),
    minimize: () => ipcRenderer.send('window:minimize'),
    maximize: () => ipcRenderer.send('window:maximize'),
    close: () => ipcRenderer.send('window:close'),
  },
  fileDialog: {
    open: (opts: any) => ipcRenderer.invoke('dialog:open', opts),
    save: (opts: any) => ipcRenderer.invoke('dialog:save', opts),
  },
})
```

### 7.5 macOS / Windows 差异

```typescript
// TitleBar.vue
<template>
  <div class="titlebar" :class="{ 'is-mac': isMac, 'is-win': isWin }">
    <!-- macOS: traffic light 按钮原生，无需自定义控制按钮 -->
    <div v-if="isMac" class="titlebar-mac">
      <span class="titlebar-title">{{ title }}</span>
    </div>
    <!-- Windows: 自定义最小化/最大化/关闭按钮 -->
    <div v-if="isWin" class="titlebar-win">
      <span class="titlebar-title">{{ title }}</span>
      <div class="titlebar-controls">
        <button @click="minimize">—</button>
        <button @click="maximize">□</button>
        <button class="close-btn" @click="close">✕</button>
      </div>
    </div>
  </div>
</template>
```

---

## 8. 性能优化方案

### 8.1 虚拟滚动 — 大量消息渲染

```typescript
// composables/useMessageVirtualList.ts
import { useVirtualizer } from '@tanstack/vue-virtual'

export function useMessageVirtualList(
  messageIds: Ref<string[]>,
  containerRef: Ref<HTMLElement | null>,
) {
  const virtualizer = useVirtualizer(computed(() => ({
    count: messageIds.value.length,
    getScrollElement: () => containerRef.value,
    estimateSize: () => 120,
    overscan: 5,
    measureElement: (el) => el.getBoundingClientRect().height, // 动态测量
  })))

  // 高度预估策略（加速初始渲染）
  // - 纯文本消息: ~80px
  // - 含产品卡片: ~280px
  // - 含 BOM 表格: ~400px
  // - 含对比面板: ~600px

  function scrollToBottom(smooth = true) {
    containerRef.value?.scrollTo({
      top: virtualizer.value.getTotalSize(),
      behavior: smooth ? 'smooth' : 'auto',
    })
  }

  return {
    virtualizer,
    scrollToBottom,
    virtualItems: computed(() => virtualizer.value.getVirtualItems()),
  }
}
```

### 8.2 BOM 表格大数据量处理 — Web Worker

```typescript
// workers/bom.worker.ts
self.onmessage = (e: MessageEvent<{
  type: 'sort' | 'filter' | 'group'
  data: BomItem[]
  params: any
}>) => {
  switch (e.data.type) {
    case 'sort': {
      const { key, order } = e.data.params
      const sorted = [...e.data.data].sort((a, b) =>
        order === 'asc' ? a[key] - b[key] : b[key] - a[key]
      )
      self.postMessage({ type: 'result', data: sorted })
      break
    }
    case 'filter': {
      const { filters } = e.data.params
      const filtered = e.data.data.filter(item =>
        Object.entries(filters).every(([k, v]) =>
          String(item[k]).toLowerCase().includes(String(v).toLowerCase())
        )
      )
      self.postMessage({ type: 'result', data: filtered })
      break
    }
    case 'group': {
      const { key } = e.data.params
      const groups = new Map()
      e.data.data.forEach(item => {
        const k = item[key]
        if (!groups.has(k)) groups.set(k, [])
        groups.get(k).push(item)
      })
      self.postMessage({ type: 'result', data: Array.from(groups.entries()) })
      break
    }
  }
}
```

### 8.3 组件级懒加载

```typescript
// 路由级懒加载
const routes = [
  { path: '/', component: () => import('@/features/chat/components/ChatView.vue') },
  { path: '/bom', component: () => import('@/features/bom/components/BomView.vue') },
]

// 交互密集型组件异步加载
const ComparisonPanel = defineAsyncComponent({
  loader: () => import('@/features/comparison/components/ComparisonPanel.vue'),
  loadingComponent: SkeletonLoader,
  delay: 200, // 200ms 后显示 loading（避免闪烁）
})

const BomCostChart = defineAsyncComponent({
  loader: () => import('@/features/bom/components/BomCostChart.vue'),
  loadingComponent: SkeletonLoader,
})
```

### 8.4 渲染性能检查清单

| 优化项 | 实现方式 | 目标指标 |
|--------|----------|----------|
| 虚拟滚动 | @tanstack/vue-virtual | 10000+ 消息不卡顿 |
| BOM 大数据排序 | Web Worker | 10000行 < 500ms |
| 打字机动画 | RAF 批量 + CSS `will-change` | 60fps 无掉帧 |
| 产品图片 | 懒加载 + IntersectionObserver + WebP | LCP < 1.5s |
| Markdown 渲染 | 按需渲染（仅可见段落） | 首次渲染 < 50ms |
| 主题切换 | CSS 变量 + 无闪烁方案 | 切换 < 16ms |
| 包体积 | Tree-shaking + 代码分割 | 首屏 JS < 500KB |
| 内存 | WeakMap 缓存 + 及时销毁 | 长会话 < 200MB |

---

## 9. 关键技术难点实现方案

### 9.1 难点一：流式打字机 + 实时 Markdown 渲染

**问题描述**：
流式文本逐 token 到达，需要实时渲染 Markdown（代码块、表格、列表等），但 Markdown 解析器通常需要完整输入。同时打字机效果要求平滑的逐字展示。

**核心矛盾**：Markdown 语法是不完整时（如 `**bold` 只有开头），直接渲染会产生闪烁或错误。

**解决方案 — 分段渲染 + 安全边界**：

```
文本分段示意：

  ┌────────────── 完整 Markdown 渲染区域 ──────────┐┬── 纯文本 ──┐
  │                                                ││            │
  │ ## 推荐方案                                     ││ 正在分析   │
  │                                                ││            │
  │ 根据您的需求，推荐以下产品：                      ││ **         │  ← 不完整 Markdown
  │                                                ││            │
  │ | 产品    | 价格  | 匹配度 |                     ││            │
  │ |---------|-------|--------|                    ││            │
  │ | AC-8000 | ¥50K  | 95%    |                    ││            │
  │                                                ││            │
  └────────────────────────────────────────────────┘┴────────────┘
              ↑ 安全边界 (safeBoundary)          ↑ 光标位置
```

```typescript
// composables/useStreamingMarkdown.ts

export function useStreamingMarkdown(speed: Ref<number>) {
  const rawContent = ref('')        // SSE 累积的完整文本
  const displayContent = ref('')    // 打字机逐步展示的文本
  const isComplete = ref(false)

  const renderResult = computed(() => {
    const safeBoundary = findLastSafeBoundary(displayContent.value)

    // 稳定部分 → Markdown 渲染
    const stableHTML = marked.parse(
      displayContent.value.slice(0, safeBoundary),
      { breaks: true, gfm: true }
    )

    // 不稳定部分 → 纯文本转义 + 光标
    const unstableText = displayContent.value.slice(safeBoundary)
    const cursorHTML = isComplete.value ? '' : '<span class="cursor-blink">▌</span>'

    return {
      stableHTML,
      totalHTML: stableHTML + escapeHTML(unstableText) + cursorHTML,
    }
  })

  /**
   * 安全渲染边界查找
   * 找到最后一个完整的 Markdown 结构终止位置
   */
  function findLastSafeBoundary(text: string): number {
    const patterns = [
      /\n\n(?=[^\n]*$)/,           // 段落分隔（已完成段落）
      /```\s*\n(?=[^`]*$)/,        // 代码块结束
      /\|\s*\n(?=[^|]*$)/,         // 表格行结束
      /\n(?=[-\*]\s)/,             // 新列表项开始
    ]

    let lastSafe = 0
    for (const pattern of patterns) {
      const matches = [...text.matchAll(new RegExp(pattern.source, 'g'))]
      if (matches.length > 0) {
        const pos = matches[matches.length - 1].index! + matches[matches.length - 1][0].length
        lastSafe = Math.max(lastSafe, pos)
      }
    }

    // 无安全边界时，回退到最后一个空格（避免渲染半个单词）
    if (lastSafe === 0) {
      const lastSpace = text.lastIndexOf(' ')
      return lastSpace > 0 ? lastSpace : text.length
    }
    return lastSafe
  }

  // RAF 驱动的打字机调度器
  let animationFrameId: number | null = null
  function tick() {
    if (displayContent.value.length < rawContent.value.length) {
      const charsPerFrame = getCharsPerFrame(speed.value)
      displayContent.value = rawContent.value.slice(
        0,
        displayContent.value.length + charsPerFrame
      )
      animationFrameId = requestAnimationFrame(tick)
    } else {
      isComplete.value = true
    }
  }

  return { rawContent, displayContent, renderResult, isComplete, startTyping: tick }
}

// 速度映射：1-5级 → 每帧字符数
function getCharsPerFrame(speed: number): number {
  return { 1: 1, 2: 2, 3: 5, 4: 10, 5: 20 }[speed] ?? 5
}

function escapeHTML(text: string): string {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}
```

**关键优化总结**：
1. **分段渲染**：文本分为「安全区域」(Markdown) 和「不安全区域」(纯文本)
2. **RAF 调度**：`requestAnimationFrame` 保证与浏览器渲染帧同步
3. **批量 Token**：多个 token 合并到一帧更新，避免过度渲染

---

### 9.2 难点二：消息列表虚拟滚动 + 动态高度 + 流式增长

**问题描述**：
聊天消息高度不固定（纯文本 ~80px，产品卡 300px+，BOM 表格 400px+），流式消息高度持续增长。虚拟滚动要求知道总高度，但动态高度会导致滚动位置跳变。

**核心矛盾**：
- 流式消息高度不断变化 → 虚拟滚动总高度重算 → 滚动位置跳变
- 用户滚动查看历史时 → 新消息来 → 不应该自动滚到底部

**解决方案**：

```typescript
// composables/useChatVirtualScroll.ts

export function useChatVirtualScroll(
  messages: Ref<ChatMessage[]>,
  containerRef: Ref<HTMLElement | null>,
) {
  const isUserScrolledUp = ref(false)
  const HEIGHT_CACHE = new Map<string, number>()

  // 智能预估高度
  function estimateMessageHeight(msg: ChatMessage): number {
    const cached = HEIGHT_CACHE.get(msg.id)
    if (cached) return cached

    if (msg.widget) {
      switch (msg.widget.type) {
        case 'product_list': return 320 + (msg.widget.items?.length ?? 0) * 280
        case 'bom':          return Math.min(600, 100 + (msg.widget.items?.length ?? 0) * 48)
        case 'comparison':   return 500
        case 'quote':        return 350
        default:             return 200
      }
    }
    return Math.max(60, Math.ceil((msg.content?.length ?? 0) / 80) * 24 + 40)
  }

  const virtualizer = useVirtualizer(computed(() => ({
    count: messages.value.length,
    getScrollElement: () => containerRef.value,
    estimateSize: (i) => estimateMessageHeight(messages.value[i]),
    overscan: 5,
    measureElement: (el) => {
      const height = el.getBoundingClientRect().height
      const msgId = el.getAttribute('data-message-id')
      if (msgId && height > 0) HEIGHT_CACHE.set(msgId, height)
      return height
    },
  })))

  // 检测用户是否主动上滚
  function onScroll(e: Event) {
    const target = e.target as HTMLElement
    const atBottom = target.scrollHeight - target.scrollTop - target.clientHeight < 100
    isUserScrolledUp.value = !atBottom
  }

  // 智能自动滚底
  function smartScrollToBottom() {
    if (!isUserScrolledUp.value) {
      nextTick(() => scrollToBottom(false)) // 流式更新用 instant 避免累积动画
    }
  }

  // 监听消息变化 → 智能滚底
  watch(
    () => messages.value.length,
    () => {
      // 新消息始终滚底
      isUserScrolledUp.value = false
      nextTick(() => scrollToBottom(false))
    }
  )

  // 监听最后一条消息内容变化（流式增长）
  watch(
    () => messages.value[messages.value.length - 1]?.content,
    smartScrollToBottom
  )

  return {
    virtualizer,
    virtualItems: computed(() => virtualizer.value.getVirtualItems()),
    scrollToBottom,
    onScroll,
    isUserScrolledUp: readonly(isUserScrolledUp),
  }
}
```

**关键策略**：
1. **高度缓存**：已渲染过的消息缓存实际高度，避免重新计算
2. **智能滚底**：用户上滚时暂停自动滚底，新消息到来时恢复
3. **instant 滚动**：流式更新期间用 `behavior: 'auto'` 避免累积动画
4. **预估值优化**：根据消息内容类型给出接近真实的预估高度

---

### 9.3 难点三：Widget 流式渲染（产品卡/BOM 逐字段填充）

**问题描述**：
AI 生成结构化 Widget（产品推荐卡、BOM 表格）时，数据是逐步到达的。客户端需要在数据不完整时展示骨架/占位，数据完整后平滑过渡到完整 UI。

**核心矛盾**：
- Widget 数据不完整时渲染什么？（空白？骨架？部分数据？）
- 如何优雅地从"加载中"过渡到"完整展示"？

**解决方案 — Widget 三态渲染**：

```
Widget 生命周期状态机：

  ┌──────────┐    create     ┌──────────┐    update    ┌──────────┐   complete   ┌──────────┐
  │  NULL    │──────────────▶│ LOADING  │─────────────▶│ PARTIAL  │─────────────▶│ COMPLETE │
  │ (无Widget)│               │ (骨架屏) │              │ (部分数据)│              │ (完整)   │
  └──────────┘               └──────────┘              └──────────┘              └──────────┘
                                                           │                         │
                                                           │    update (多次)        │
                                                           └─────────────────────────┘
```

```typescript
// components shared/WidgetContainer.vue
// 通用 Widget 容器，处理三态渲染

<script setup lang="ts">
interface WidgetContainerProps {
  widget: {
    id: string
    type: string              // 'product_list' | 'bom' | 'comparison' | 'quote'
    action: 'create' | 'update' | 'complete' | 'error'
    data: any                 // 部分或完整数据
  } | null
}

const props = defineProps<WidgetContainerProps>()

const state = computed<'empty' | 'loading' | 'partial' | 'complete' | 'error'>(() => {
  if (!props.widget) return 'empty'
  switch (props.widget.action) {
    case 'create': return 'loading'
    case 'update': return 'partial'
    case 'complete': return 'complete'
    case 'error':   return 'error'
    default:        return 'empty'
  }
})
</script>

<template>
  <Transition name="widget-fade" mode="out-in">
    <!-- 加载态：骨架屏 -->
    <div v-if="state === 'loading'" key="loading" class="widget-loading">
      <slot name="skeleton">
        <SkeletonLoader :type="widget?.type" />
      </slot>
    </div>

    <!-- 局部态：部分数据 + 微骨架 -->
    <div v-else-if="state === 'partial'" key="partial" class="widget-partial">
      <slot name="widget" :data="widget?.data" :isPartial="true" />
      <div class="partial-indicator">
        <el-progress :percentage="undefined" :indeterminate="true" :duration="3" />
      </div>
    </div>

    <!-- 完成态：完整 Widget -->
    <div v-else-if="state === 'complete'" key="complete" class="widget-complete">
      <slot name="widget" :data="widget?.data" :isPartial="false" />
    </div>

    <!-- 错误态 -->
    <div v-else-if="state === 'error'" key="error" class="widget-error">
      <el-result icon="error" title="Widget 加载失败" sub-title="请重试或刷新页面">
        <template #extra>
          <el-button @click="$emit('retry')">重试</el-button>
        </template>
      </el-result>
    </div>
  </Transition>
</template>

<style scoped>
.widget-fade-enter-active,
.widget-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.widget-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.widget-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
```

**配合 streamingStore 的 Widget 累积更新**：

```typescript
// stores/streamingStore.ts 中的 Widget 处理

function handleWidgetChunk(chunk: SSEWidgetData) {
  const existing = this.partialWidgets.find(w => w.widgetId === chunk.widgetId)

  if (!existing) {
    // CREATE: 新建 Widget，进入 loading 态
    this.partialWidgets.push({
      widgetId: chunk.widgetId,
      type: chunk.type,
      action: 'create',
      data: chunk.data,
    })
    // 同时写入 chatStore 的消息 Widget 引用
    chatStore.attachWidget(chunk.messageId, {
      id: chunk.widgetId,
      type: chunk.type,
      action: 'create',
      data: chunk.data,
    })
  } else {
    // UPDATE: 合并数据
    // 关键：对 product_list 这种数组类型，需要追加而非覆盖
    if (existing.type === 'widget.product_list' && chunk.data.items) {
      existing.data.items = [...(existing.data.items || []), ...chunk.data.items]
    } else {
      Object.assign(existing.data, chunk.data)
    }
    existing.action = chunk.action
    // 同步更新 chatStore 中的 Widget 引用
    chatStore.updateWidget(chunk.messageId, chunk.widgetId, existing)
  }

  // COMPLETE: 标记完成
  if (chunk.action === 'complete') {
    chatStore.finalizeWidget(chunk.messageId, chunk.widgetId)
  }
}
```

**关键策略**：
1. **三态渲染**：loading（骨架屏）→ partial（部分数据+进度条）→ complete（完整 UI）
2. **数据累积合并**：对数组数据追加而非覆盖
3. **Transition 动画**：状态切换间 300ms fade + slide 动画
4. **乐观显示**：partial 状态也展示已有数据，用户体验更好

---

## 附录 A：核心类型定义汇总

```typescript
// types/message.ts — 消息核心类型

interface ChatMessage {
  id: string
  sessionId: string
  role: 'user' | 'assistant' | 'system'
  content: string
  createdAt: string
  status: 'sending' | 'sent' | 'streaming' | 'completed' | 'error'
  /** 思考过程（仅 AI） */
  thinkingSteps?: ThinkingStep[]
  /** 结构化 Widget */
  widget?: {
    id: string
    type: 'product_list' | 'bom' | 'comparison' | 'quote'
    action: 'create' | 'update' | 'complete' | 'error'
    data: any
  } | null
  /** 预估渲染高度 */
  estimatedHeight?: number
  /** 错误信息 */
  error?: { code: string; message: string }
  /** 附件 */
  attachments?: Array<{ name: string; url: string; type: string; size: number }>
}

interface ThinkingStep {
  id: string
  title: string
  status: 'pending' | 'running' | 'completed' | 'error'
  description?: string
  duration?: number
}

interface SSEChunk {
  type: SSEEventType
  messageId?: string
  [key: string]: any
}
```

## 附录 B：主题切换无闪烁方案

```css
/* 防止主题切换闪烁 */
html {
  /* 通过 script 标签在 <head> 中提前设置 */
  color-scheme: light dark;
}

/* 使用 CSS 变量，切换时无重绘 */
:root {
  --color-bg: #ffffff;
  --color-text: #1a1a1a;
  /* ... */
}

:root.dark {
  --color-bg: #0f0f0f;
  --color-text: #e5e5e5;
  /* ... */
}

/* 过渡动画 */
* {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}

/* 但在首次加载时禁用过渡（避免页面闪动） */
.no-transitions * {
  transition: none !important;
}
```

```html
<!-- index.html <head> 中内联脚本 -->
<script>
  // 在 DOM 渲染前执行，避免闪烁
  (function() {
    const stored = localStorage.getItem('theme')
    const prefersDark = matchMedia('(prefers-color-scheme: dark)').matches
    const theme = stored === 'system'
      ? (prefersDark ? 'dark' : 'light')
      : (stored || 'system') === 'dark' ? 'dark' : 'light'

    document.documentElement.classList.add(theme)
    // 添加 'no-transitions' 类防止首次加载过渡动画
    document.documentElement.classList.add('no-transitions')
    // 页面加载完成后移除
    window.addEventListener('load', () => {
      document.documentElement.classList.remove('no-transitions')
    })
  })()
</script>
```

---

> **文档状态**: ✅ 完整  
> **下次更新**: 实现过程中根据实际遇到的问题补充  
> **关联文档**: `design/CPQ_Agent_App_方案设计.md`
