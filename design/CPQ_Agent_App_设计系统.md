# CPQ Agent App — 视觉设计系统文档

> **应用**：AI 配单桌面 App（Vue 3 + Element Plus）
> **平台**：macOS / Windows（Electron）
> **背景**：制造业 CPQ（Configure-Price-Quote）场景
> **版本**：v1.0

---

## 1. 设计原则（Design Principles）

> **专业 · 现代 · 信赖感**

**1. 信息层级优先** — 制造业配置场景信息密度高，每个界面必须建立清晰的视觉层级：配置对话 > 产品参数 > 价格信息 > 辅助操作。用户视线路径由主到次，不迷失。

**2. 数据驱动可视化** — 产品参数、BOM、报价是决策核心。使用表格、标签、色标将结构化数据转化为一目了然的信息——不牺牲精确性换取美观。

**3. 对话即工作流** — AI 配单的本质是"对话驱动的配置引擎"。UI 应让用户感觉在跟一位资深工程师交谈，聊天区域是主要工作区而非附属功能。

**4. 信任感源自一致性** — 制造业客户对大屏投影、会议室演示、笔记本使用等多场景敏感。所有组件的交互行为、色彩映射、动效曲线在整个应用中保持一致，消除不确定性。

**5. 可访问性即专业度** — 符合 WCAG AA 标准（对比度 ≥ 4.5:1），支持键盘全导航，考虑色弱用户的色彩使用——这是制造业企业级软件的底线要求。

---

## 2. 色彩系统（Color System）

### 2.1 设计策略

在 Element Plus 的 `--el-color-primary` 等 CSS 变量体系上扩展，而非另起炉灶。新增 **CPQ 专属语义色**（匹配度、价格高亮、差异提示）和 **功能区域色**（对话气泡、产品卡片、侧边栏）。

**主色选型理由**：
- 选用 `#2563EB`（Tailwind blue-600）而非 Element Plus 默认 `#409EFF`——更深的蓝传递专业与信赖感，在大屏投影环境下辨识度更高
- 辅以 `#0EA5E9`（sky-500）作为科技感点缀，暗示 AI / 智能

### 2.2 完整 CSS 变量定义

```css
/* =============================================
   CPQ Agent App — Design Tokens
   Element Plus Compatible Extension
   ============================================= */

/* ---------- Light Theme (默认亮色) ---------- */
:root {
  /* -- Primary Color Base (覆盖 Element Plus 主色) -- */
  --el-color-primary: #2563eb;          /* 主色 - 专业信赖 */
  --el-color-primary-light-3: #60a5fa;
  --el-color-primary-light-5: #93c5fd;
  --el-color-primary-light-7: #bfdbfe;
  --el-color-primary-light-8: #dbeafe;
  --el-color-primary-light-9: #eff6ff;
  --el-color-primary-dark-2: #1d4ed8;

  /* -- Secondary / Accent -- */
  --cpq-color-accent: #0ea5e9;          /* AI / 智能点缀 */
  --cpq-color-accent-light: #7dd3fc;
  --cpq-color-accent-dark: #0284c7;

  /* -- Semantic Colors (覆盖 Element Plus) -- */
  --el-color-success: #059669;          /* 成功 / 已配置完成 */
  --el-color-success-light-3: #34d399;
  --el-color-success-light-9: #ecfdf5;
  --el-color-warning: #d97706;          /* 警告 / 需关注 */
  --el-color-warning-light-3: #fbbf24;
  --el-color-warning-light-9: #fffbeb;
  --el-color-danger: #dc2626;           /* 错误 / 不可行 */
  --el-color-danger-light-3: #f87171;
  --el-color-danger-light-9: #fef2f2;
  --el-color-error: #dc2626;
  --el-color-error-light-3: #f87171;
  --el-color-error-light-9: #fef2f2;
  --el-color-info: #6b7280;
  --el-color-info-light-3: #9ca3af;
  --el-color-info-light-9: #f3f4f6;

  /* -- CPQ 专属语义色 -- */
  --cpq-color-match-high: #059669;      /* 匹配度 ≥ 90% 强匹配 */
  --cpq-color-match-medium: #d97706;    /* 匹配度 60-89% */
  --cpq-color-match-low: #dc2626;       /* 匹配度 < 60% */
  --cpq-color-price-highlight: #dc2626; /* 价格高亮（降价的绿/涨价的红） */
  --cpq-color-price-primary: #111827;   /* 金额主色 */
  --cpq-color-diff-added: #059669;      /* 方案对比 - 新增项 */
  --cpq-color-diff-removed: #dc2626;    /* 方案对比 - 减少项 */
  --cpq-color-diff-changed: #d97706;    /* 方案对比 - 变更项 */

  /* -- Neutral / Gray Scale (覆盖 Element Plus) -- */
  --el-color-white: #ffffff;
  --el-color-black: #000000;

  /* Text colors */
  --el-text-color-primary: #111827;      /* 主要文字 接近黑 */
  --el-text-color-regular: #374151;      /* 常规正文 */
  --el-text-color-secondary: #6b7280;    /* 辅助信息 */
  --el-text-color-placeholder: #9ca3af;  /* 占位符 */
  --el-text-color-disabled: #d1d5db;     /* 禁用文字 */

  /* Border colors */
  --el-border-color: #d1d5db;           /* 默认边框 */
  --el-border-color-light: #e5e7eb;     /* 浅边框 */
  --el-border-color-lighter: #f3f4f6;   /* 更浅边框 */
  --el-border-color-extra-light: #f9fafb;
  --el-border-color-dark: #9ca3af;      /* 深边框 */
  --el-border-color-darker: #6b7280;

  /* Fill / Background */
  --el-fill-color: #f3f4f6;
  --el-fill-color-light: #f9fafb;
  --el-fill-color-lighter: #fcfcfc;
  --el-fill-color-extra-light: #fefefe;
  --el-fill-color-dark: #e5e7eb;
  --el-fill-color-darker: #d1d5db;
  --el-fill-color-blank: #ffffff;

  /* Page & Overlay backgrounds */
  --el-bg-color: #ffffff;
  --el-bg-color-page: #f0f2f5;          /* 页面背景 */
  --el-bg-color-overlay: #ffffff;

  /* -- CPQ 组件区域专用色 -- */
  --cpq-bg-chat: #f8fafc;               /* 聊天区域背景 */
  --cpq-bg-sidebar: #f1f5f9;            /* 侧边栏背景 */
  --cpq-bg-card: #ffffff;               /* 产品卡片背景 */
  --cpq-bg-card-hover: #f8fafc;         /* 卡片 hover */
  --cpq-bg-bom-header: #f1f5f9;         /* BOM 表头 */
  --cpq-bg-bom-row-hover: #f0fdf4;      /* BOM 行 hover */
  --cpq-bg-bom-row-even: #fafafa;       /* BOM 斑马行 */
  --cpq-bg-message-user: #dbeafe;       /* 用户消息气泡 */
  --cpq-bg-message-agent: #ffffff;       /* Agent 消息气泡 */
  --cpq-bg-message-thinking: #f0f9ff;   /* 思考过程背景 */
  --cpq-bg-tag-match-high: #f0fdf4;     /* 高匹配标签 bg */
  --cpq-bg-tag-match-medium: #fffbeb;   /* 中匹配标签 bg */
  --cpq-bg-tag-match-low: #fef2f2;      /* 低匹配标签 bg */
  --cpq-bg-code-inline: #f1f5f9;        /* 行内代码 */
  --cpq-border-card: #e2e8f0;           /* 卡片边框 */
  --cpq-border-chat-bubble: #e2e8f0;    /* 消息气泡边框 */
  --cpq-border-divider: #e5e7eb;        /* 分割线 */

  /* -- Shadows -- */
  --el-box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --el-box-shadow-light: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --el-box-shadow-lighter: 0 0 2px 0 rgb(0 0 0 / 0.03);
  --el-box-shadow-dark: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --cpq-shadow-card: 0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06);
  --cpq-shadow-card-hover: 0 10px 15px -3px rgb(0 0 0 / 0.08), 0 4px 6px -4px rgb(0 0 0 / 0.04);
  --cpq-shadow-message: 0 1px 2px 0 rgb(0 0 0 / 0.04);
  --cpq-shadow-modal: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
}


/* ---------- Dark Theme (暗色) ---------- */
[data-theme='dark'] {
  /* -- Primary -- */
  --el-color-primary: #60a5fa;
  --el-color-primary-light-3: #3b82f6;
  --el-color-primary-light-5: #2563eb;
  --el-color-primary-light-7: #1d4ed8;
  --el-color-primary-light-8: #1e40af;
  --el-color-primary-light-9: #1e3a8a;
  --el-color-primary-dark-2: #93c5fd;

  /* -- Accent -- */
  --cpq-color-accent: #38bdf8;
  --cpq-color-accent-light: #0ea5e9;
  --cpq-color-accent-dark: #7dd3fc;

  /* -- Semantic -- */
  --el-color-success: #34d399;
  --el-color-success-light-3: #059669;
  --el-color-success-light-9: #064e3b;
  --el-color-warning: #fbbf24;
  --el-color-warning-light-3: #d97706;
  --el-color-warning-light-9: #78350f;
  --el-color-danger: #f87171;
  --el-color-danger-light-3: #dc2626;
  --el-color-danger-light-9: #450a0a;
  --el-color-error: #f87171;
  --el-color-error-light-3: #dc2626;
  --el-color-error-light-9: #450a0a;
  --el-color-info: #9ca3af;
  --el-color-info-light-3: #6b7280;
  --el-color-info-light-9: #1f2937;

  /* -- CPQ 专属语义色 (暗色反转) -- */
  --cpq-color-match-high: #34d399;
  --cpq-color-match-medium: #fbbf24;
  --cpq-color-match-low: #f87171;
  --cpq-color-price-highlight: #fbbf24;
  --cpq-color-price-primary: #f9fafb;
  --cpq-color-diff-added: #34d399;
  --cpq-color-diff-removed: #f87171;
  --cpq-color-diff-changed: #fbbf24;

  /* -- Text (暗色反转) -- */
  --el-text-color-primary: #f9fafb;
  --el-text-color-regular: #d1d5db;
  --el-text-color-secondary: #9ca3af;
  --el-text-color-placeholder: #6b7280;
  --el-text-color-disabled: #374151;

  /* -- Border -- */
  --el-border-color: #374151;
  --el-border-color-light: #2d3748;
  --el-border-color-lighter: #1f2937;
  --el-border-color-extra-light: #111827;
  --el-border-color-dark: #4b5563;
  --el-border-color-darker: #6b7280;

  /* -- Fill / Background -- */
  --el-fill-color: #1f2937;
  --el-fill-color-light: #1a2332;
  --el-fill-color-lighter: #162032;
  --el-fill-color-extra-light: #111827;
  --el-fill-color-dark: #2d3748;
  --el-fill-color-darker: #374151;
  --el-fill-color-blank: #0f172a;

  /* -- Page & Overlay -- */
  --el-bg-color: #0f172a;               /* 主背景 - 深蓝黑 */
  --el-bg-color-page: #0a0f1e;          /* 页面背景更深 */
  --el-bg-color-overlay: #1a2332;       /* 弹窗 / 下拉背景 */

  /* -- CPQ 组件区域 (暗色) -- */
  --cpq-bg-chat: #0d1425;
  --cpq-bg-sidebar: #0a0f1e;
  --cpq-bg-card: #162032;
  --cpq-bg-card-hover: #1a2638;
  --cpq-bg-bom-header: #1a2332;
  --cpq-bg-bom-row-hover: rgba(37, 99, 235, 0.08);
  --cpq-bg-bom-row-even: #111827;
  --cpq-bg-message-user: #1e3a8a;        /* 深色下用户气泡用 primary dark */
  --cpq-bg-message-agent: #1a2332;
  --cpq-bg-message-thinking: rgba(14, 165, 233, 0.08);
  --cpq-bg-tag-match-high: rgba(5, 150, 105, 0.15);
  --cpq-bg-tag-match-medium: rgba(217, 119, 6, 0.15);
  --cpq-bg-tag-match-low: rgba(220, 38, 38, 0.15);
  --cpq-bg-code-inline: rgba(255, 255, 255, 0.06);
  --cpq-border-card: rgba(255, 255, 255, 0.06);
  --cpq-border-chat-bubble: rgba(255, 255, 255, 0.06);
  --cpq-border-divider: rgba(255, 255, 255, 0.06);

  /* -- Shadows (暗色更柔和) -- */
  --el-box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.4), 0 1px 2px -1px rgb(0 0 0 / 0.3);
  --el-box-shadow-light: 0 1px 2px 0 rgb(0 0 0 / 0.3);
  --el-box-shadow-lighter: 0 0 2px 0 rgb(0 0 0 / 0.2);
  --el-box-shadow-dark: 0 4px 6px -1px rgb(0 0 0 / 0.5), 0 2px 4px -2px rgb(0 0 0 / 0.3);
  --cpq-shadow-card: 0 1px 3px 0 rgb(0 0 0 / 0.3), 0 1px 2px -1px rgb(0 0 0 / 0.2);
  --cpq-shadow-card-hover: 0 4px 6px -1px rgb(0 0 0 / 0.4), 0 2px 4px -2px rgb(0 0 0 / 0.3);
  --cpq-shadow-message: 0 1px 2px 0 rgb(0 0 0 / 0.3);
  --cpq-shadow-modal: 0 20px 25px -5px rgb(0 0 0 / 0.5), 0 8px 10px -6px rgb(0 0 0 / 0.3);
}
```

### 2.3 色彩使用指南

| 用途 | 亮色色值 | 暗色色值 | 说明 |
|------|----------|----------|------|
| **主色** `--el-color-primary` | `#2563eb` | `#60a5fa` | 按钮、链接、活跃态、选中态 |
| **强调色** `--cpq-color-accent` | `#0ea5e9` | `#38bdf8` | AI 指示器、科技感装饰线 |
| **成功** `--el-color-success` | `#059669` | `#34d399` | 配置完成、报价确认 |
| **警告** `--el-color-warning` | `#d97706` | `#fbbf24` | 匹配度一般、需确认 |
| **危险** `--el-color-danger` | `#dc2626` | `#f87171` | 配置不可行、价格冲突 |
| **页面背景** `--el-bg-color-page` | `#f0f2f5` | `#0a0f1e` | 最底层背景 |
| **卡片背景** `--cpq-bg-card` | `#ffffff` | `#162032` | 内容卡片、气泡 |

---

## 3. 排版系统（Typography）

### 3.1 字体栈（中英文混排）

```css
:root {
  /* 主字体栈 */
  --el-font-family: 'Inter', -apple-system, BlinkMacSystemFont,
    'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC',
    system-ui, sans-serif;

  /* 等宽字体（用于代码、参数值） */
  --cpq-font-mono: 'JetBrains Mono', 'SF Mono', 'Fira Code',
    'Menlo', 'Consolas', monospace;

  /* 数字字体（用于金额、数字） */
  --cpq-font-num: 'Inter', 'SF Pro Display', sans-serif;
}

[data-theme='dark'] {
  /* 暗色下字体不变 */
}
```

**字重使用**：Light(300) / Regular(400) / Medium(500) / Semibold(600) / Bold(700)

### 3.2 字体层级（Type Scale）

```css
:root {
  /* 用 Element Plus 层级 + 扩展 */

  /* 大型 Display */
  --el-font-size-extra-large: 20px;      /* subtitle / 弹窗标题 */
  --cpq-font-size-2xl: 24px;             /* 大标题 */
  --cpq-font-size-3xl: 30px;             /* 报价金额大字 */
  --cpq-font-size-4xl: 36px;             /* 页面级大标题 */

  /* 常规层级 */
  --el-font-size-large: 18px;            /* 卡片标题 */
  --el-font-size-medium: 16px;           /* 面板标题 */
  --el-font-size-base: 14px;             /* 正文 */
  --el-font-size-small: 13px;            /* 辅助 / 标签 */
  --el-font-size-extra-small: 12px;      /* 脚注 / 时间戳 */

  /* 字重 */
  --el-font-weight-primary: 500;
  --cpq-font-weight-semibold: 600;
  --cpq-font-weight-bold: 700;

  /* 行高 */
  --cpq-line-height-tight: 1.25;
  --cpq-line-height-normal: 1.5;
  --cpq-line-height-relaxed: 1.75;
}
```

### 3.3 层级用法表

| Token | 尺寸 | 字重 | 行高 | 用途 |
|-------|------|------|------|------|
| `--cpq-font-size-4xl` | 36px | 700 | 1.25 | 报价总金额（大字） |
| `--cpq-font-size-3xl` | 30px | 700 | 1.25 | 方案对比头部金额 |
| `--cpq-font-size-2xl` | 24px | 600 | 1.3 | 产品卡片名称、页面标题 |
| `--el-font-size-extra-large` | 20px | 600 | 1.35 | 弹窗标题、设置面板标题 |
| `--el-font-size-large` | 18px | 500 | 1.4 | 侧边栏会话标题、分组标签 |
| `--el-font-size-medium` | 16px | 500 | 1.4 | 面板子标题、消息中重要链接 |
| `--el-font-size-base` | 14px | 400 | 1.6 | **正文默认**、消息内容、表格内容 |
| `--el-font-size-small` | 13px | 400 | 1.5 | 辅助信息、标签文本、参数名 |
| `--el-font-size-extra-small` | 12px | 400 | 1.4 | 时间戳、脚注、次要标注 |

---

## 4. 间距和布局系统（Spacing & Layout）

### 4.1 间距比例尺（基于 4px/8px 网格）

```css
:root {
  /* Base unit: 4px */
  --cpq-space-1: 4px;      /* 微间距 */
  --cpq-space-2: 8px;      /* 组件内间距（小） */
  --cpq-space-3: 12px;     /* 组件内间距 / 表单标签间距 */
  --cpq-space-4: 16px;     /* 卡片内边距 / 元素间距 */
  --cpq-space-5: 20px;     /* 微调间距 */
  --cpq-space-6: 24px;     /* 区块间距 / 卡片间距 */
  --cpq-space-8: 32px;     /* 大区块间距 */
  --cpq-space-10: 40px;    /* 页面 section 间距 */
  --cpq-space-12: 48px;    /* 页面内容与两侧的边距 */
  --cpq-space-16: 64px;    /* 大页面顶部间距 */

  /* Element Plus 兼容 (spacing 只是 placeholder, Element Plus 未定义全局 spacing) */
  --el-spacing-xs: 4px;
  --el-spacing-sm: 8px;
  --el-spacing-base: 12px;
  --el-spacing-md: 16px;
  --el-spacing-lg: 24px;
  --el-spacing-xl: 32px;
}
```

### 4.2 布局边界

| 变量 | 值 | 用途 |
|------|-----|------|
| `--cpq-sidebar-width` | 280px | 左侧侧边栏宽度 |
| `--cpq-sidebar-collapsed` | 64px | 侧边栏收起宽度 |
| `--cpq-chat-max-width` | 720px | 消息区域最大宽度（居中） |
| `--cpq-card-min-width` | 320px | 产品卡片最小宽度 |
| `--cpq-card-max-width` | 480px | 产品卡片最大宽度 |
| `--cpq-compare-min-width` | 600px | 方案对比面板最小宽度 |
| `--cpq-header-height` | 56px | 顶部标题栏高度 |
| `--cpq-input-max-width` | 680px | 聊天输入框最大宽度 |

### 4.3 布局结构（App 骨架）

```
┌─────────────────────────────────────────────────────┐
│  ─── Header (56px) ───  [APP LOGO] [新对话] [设置]  │
├──────────┬──────────────────────────────────────────┤
│          │                                          │
│ Sidebar  │        Main Content Area                 │
│ (280px)  │                                          │
│          │    ┌─────────────────────────────┐       │
│  ┌────┐  │    │     Chat Messages Area      │       │
│  │会话1│ │    │   (max-width: 720px,        │       │
│  │会话2│ │    │    centered horizontally)    │       │
│  │会话3│ │    │                             │       │
│  │ ... │ │    │   ┌─── user bubble ──┐      │       │
│  └────┘  │    │   └──────────────────┘      │       │
│          │    │                             │       │
│ [新对话]  │    │   ┌── agent bubble ──┐      │       │
│          │    │   │  ┌─ product card ┐ │     │       │
│          │    │   │  └───────────────┘ │     │       │
│          │    │   └────────────────────┘     │       │
│          │    │                             │       │
│          │    │   ┌─── Input Bar ────┐       │       │
│          │    │   │ [输入配置需求...] │       │       │
│          │    │   └──────────────────┘       │       │
│          │    └─────────────────────────────┘       │
│          │                                          │
└──────────┴──────────────────────────────────────────┘
```

---

## 5. 组件视觉规范（Component Specs）

### 5.1 消息气泡（Message Bubbles）

#### 视觉描述

| 属性 | 用户消息 | Agent 消息 | 思考过程提示 |
|------|---------|-----------|-------------|
| 背景色 | `var(--cpq-bg-message-user)` | `var(--cpq-bg-message-agent)` | `var(--cpq-bg-message-thinking)` |
| 文字色 | `var(--el-text-color-primary)` | `var(--el-text-color-regular)` | `var(--el-text-color-secondary)` |
| 对齐 | 右对齐 | 左对齐 | 左对齐 |
| 圆角 | `12px 4px 12px 12px` | `4px 12px 12px 12px` | `8px` |
| 阴影 | `var(--cpq-shadow-message)` | `var(--cpq-shadow-message)` | none |
| 边框 | 无 | `1px solid var(--cpq-border-chat-bubble)` | `1px dashed var(--el-color-primary-light-5)` |
| 边距 | 右侧 `8px` | 左侧 `8px` | 左右各 `24px` |
| 时间戳 | 消息下方，`--el-font-size-extra-small`，`--el-text-color-placeholder` | 同左 | 不展示 |
| 头像 | 可选用户图标（36px） | AI 图标（36px） | 不展示 |

#### 关键 CSS

```css
/* 消息容器 - 实现左右对齐 */
.cpq-message {
  display: flex;
  gap: var(--cpq-space-3);
  margin-bottom: var(--cpq-space-4);
  animation: messageSlideIn 0.3s ease-out;
}

.cpq-message--user {
  flex-direction: row-reverse;
}

.cpq-message--agent {
  flex-direction: row;
}

/* 消息气泡 */
.cpq-message__bubble {
  max-width: 600px;
  padding: var(--cpq-space-3) var(--cpq-space-4);
  font-size: var(--el-font-size-base);
  line-height: var(--cpq-line-height-normal);
  word-break: break-word;
}

.cpq-message--user .cpq-message__bubble {
  background: var(--cpq-bg-message-user);
  color: var(--el-text-color-primary);
  border-radius: 12px 4px 12px 12px;
  box-shadow: var(--cpq-shadow-message);
}

.cpq-message--agent .cpq-message__bubble {
  background: var(--cpq-bg-message-agent);
  color: var(--el-text-color-regular);
  border-radius: 4px 12px 12px 12px;
  border: 1px solid var(--cpq-border-chat-bubble);
  box-shadow: var(--cpq-shadow-message);
}

/* 思考过程提示（流式输出中可折叠） */
.cpq-message-thinking {
  display: flex;
  align-items: center;
  gap: var(--cpq-space-2);
  padding: var(--cpq-space-2) var(--cpq-space-4);
  margin: var(--cpq-space-2) 0;
  margin-left: 44px;  /* 对齐 agent 消息的左边 */
  font-size: var(--el-font-size-small);
  color: var(--el-text-color-secondary);
  background: var(--cpq-bg-message-thinking);
  border: 1px dashed var(--el-color-primary-light-5);
  border-radius: 8px;
  cursor: pointer;
  transition: all var(--el-transition-duration-fast);
}

/* 思考过程脉冲点 */
.cpq-thinking-dot {
  display: inline-flex;
  gap: 3px;
}
.cpq-thinking-dot::before,
.cpq-thinking-dot::after {
  content: '';
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--el-color-primary);
  animation: dotPulse 1.4s infinite ease-in-out both;
}
.cpq-thinking-dot::before {
  animation-delay: -0.32s;
}
.cpq-thinking-dot::after {
  animation-delay: -0.16s;
}

@keyframes dotPulse {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}
```

---

### 5.2 产品卡片（Product Card）

#### 视觉描述

产品卡片是 Agent 推荐产品时的富卡片渲染，包含：
- **顶部**：产品图片（240×180px，object-cover）或占位图
- **标题行**：产品名称（large 18px Semibold）+ 匹配度标签
- **参数行**：关键参数表格（2列，参数名+参数值）
- **价格行**：单价 / 批量价（medium 16px Semibold）
- **操作行**：选择 / 查看详情 / 对比按钮

**匹配度标签设计**：
- 90-100%：`--cpq-color-match-high` + 实心填充 + "极佳匹配" 文字
- 60-89%：`--cpq-color-match-medium` + 实心填充 + "良好匹配" 文字
- <60%：`--cpq-color-match-low` + 实心填充 + "一般匹配" 文字

#### 关键 CSS

```css
.cpq-product-card {
  background: var(--cpq-bg-card);
  border: 1px solid var(--cpq-border-card);
  border-radius: 12px;
  box-shadow: var(--cpq-shadow-card);
  overflow: hidden;
  transition: all var(--el-transition-duration);
  margin: var(--cpq-space-3) 0;
}

.cpq-product-card:hover {
  box-shadow: var(--cpq-shadow-card-hover);
  transform: translateY(-2px);
  border-color: var(--el-color-primary-light-5);
}

.cpq-product-card__image {
  width: 100%;
  height: 180px;
  object-fit: cover;
  background: var(--el-fill-color);
}

.cpq-product-card__body {
  padding: var(--cpq-space-4);
}

.cpq-product-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--cpq-space-3);
}

.cpq-product-card__title {
  font-size: var(--el-font-size-large);
  font-weight: var(--cpq-font-weight-semibold);
  color: var(--el-text-color-primary);
  line-height: var(--cpq-line-height-tight);
}

/* 匹配度标签 */
.cpq-match-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: var(--el-font-size-extra-small);
  font-weight: var(--cpq-font-weight-semibold);
  line-height: 1.4;
  white-space: nowrap;
}

.cpq-match-tag--high {
  color: var(--cpq-color-match-high);
  background: var(--cpq-bg-tag-match-high);
  border: 1px solid var(--cpq-color-match-high);
}

.cpq-match-tag--medium {
  color: var(--cpq-color-match-medium);
  background: var(--cpq-bg-tag-match-medium);
  border: 1px solid var(--cpq-color-match-medium);
}

.cpq-match-tag--low {
  color: var(--cpq-color-match-low);
  background: var(--cpq-bg-tag-match-low);
  border: 1px solid var(--cpq-color-match-low);
}

/* 参数表格 */
.cpq-product-card__params {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--cpq-space-2) var(--cpq-space-4);
  margin-bottom: var(--cpq-space-3);
  padding: var(--cpq-space-3);
  background: var(--el-fill-color);
  border-radius: 8px;
}

.cpq-param__label {
  font-size: var(--el-font-size-small);
  color: var(--el-text-color-secondary);
}

.cpq-param__value {
  font-size: var(--el-font-size-base);
  color: var(--el-text-color-primary);
  font-weight: var(--cpq-font-weight-semibold);
  text-align: right;
}

/* 价格 */
.cpq-product-card__price {
  font-size: var(--el-font-size-medium);
  font-weight: var(--cpq-font-weight-bold);
  color: var(--cpq-color-price-primary);
  margin-bottom: var(--cpq-space-3);
}

.cpq-product-card__price-unit {
  font-size: var(--el-font-size-small);
  font-weight: var(--el-font-weight-primary);
  color: var(--el-text-color-secondary);
  margin-left: var(--cpq-space-1);
}

/* 操作按钮 */
.cpq-product-card__actions {
  display: flex;
  gap: var(--cpq-space-2);
  justify-content: flex-end;
}

.cpq-product-card .el-button--primary {
  --el-button-bg-color: var(--el-color-primary);
  --el-button-text-color: white;
  --el-button-hover-bg-color: var(--el-color-primary-dark-2);
  font-weight: 500;
  padding: var(--cpq-space-2) var(--cpq-space-4);
  border-radius: 6px;
}

.cpq-product-card .el-button--default {
  padding: var(--cpq-space-2) var(--cpq-space-4);
  border-radius: 6px;
}


### 5.3 BOM 表格（Bill of Materials Table）

#### 视觉描述

- 紧凑表格，以 Element Plus `el-table` 为基础定制
- **列结构**：序号 | 物料编码 | 物料名称 | 规格型号 | 数量 | 单位 | 单价 | 金额
- 数字列（数量 / 单价 / 金额）：**右对齐**，等宽字体 `--cpq-font-mono`
- 金额列高亮：`--cpq-color-price-primary` 字色，`--cpq-font-weight-bold` 字重
- 合计行：背景 `--el-color-primary-light-9`（暗色：`--el-fill-color`），上下粗边框（2px）
- 折叠行：支持按"组件"分组折叠，折叠箭头在左侧

#### 关键 CSS

```css
.cpq-bom-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--el-font-size-small);
  margin: var(--cpq-space-3) 0;
}

.cpq-bom-table thead th {
  background: var(--cpq-bg-bom-header);
  padding: var(--cpq-space-2) var(--cpq-space-3);
  font-weight: var(--cpq-font-weight-semibold);
  color: var(--el-text-color-primary);
  text-align: left;
  border-bottom: 2px solid var(--el-border-color);
  font-size: var(--el-font-size-small);
}

.cpq-bom-table thead th.cpq-bom-table__col-num {
  text-align: right;
}

/* 数字列右对齐 */
.cpq-bom-table td.cpq-bom-table__col-price,
.cpq-bom-table td.cpq-bom-table__col-qty,
.cpq-bom-table td.cpq-bom-table__col-amount {
  text-align: right;
  font-family: var(--cpq-font-mono);
  font-variant-numeric: tabular-nums;
}

/* 金额高亮 */
.cpq-bom-table td.cpq-bom-table__col-amount {
  font-weight: var(--cpq-font-weight-semibold);
  color: var(--cpq-color-price-primary);
}

/* 斑马行 */
.cpq-bom-table tbody tr:nth-child(even) {
  background: var(--cpq-bg-bom-row-even);
}

.cpq-bom-table tbody tr:hover {
  background: var(--cpq-bg-bom-row-hover);
}

.cpq-bom-table tbody td {
  padding: var(--cpq-space-2) var(--cpq-space-3);
  border-bottom: 1px solid var(--el-border-color-lighter);
}

/* 合计行 */
.cpq-bom-table tfoot tr.cpq-bom-table__total td {
  border-top: 2px solid var(--el-color-primary);
  border-bottom: 2px solid var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  padding: var(--cpq-space-3);
  font-weight: var(--cpq-font-weight-bold);
}

[data-theme='dark'] .cpq-bom-table tfoot tr.cpq-bom-table__total td {
  background: var(--el-fill-color);
}

/* 折叠行展开/收起箭头 */
.cpq-bom-table__expand {
  cursor: pointer;
  transition: transform var(--el-transition-duration-fast);
  color: var(--el-text-color-secondary);
  margin-right: var(--cpq-space-2);
}

.cpq-bom-table__expand.is-expanded {
  transform: rotate(90deg);
}
```


### 5.4 方案对比面板（Comparison Panel）

#### 视觉描述

- **布局**：A | B 双列布局，中间一条 1px 分割线
- **顶部**：方案标题（方案A / 方案B），各列标题置顶
- **每行结构**：参数名称 | 方案A 值 | 分隔线 | 方案B 值
- **差异高亮**：
  - 值不同时，差异方着色背景 + 左侧 3px 彩色边框
  - 新增项 `--cpq-color-diff-added`（绿色系）
  - 减少项 `--cpq-color-diff-removed`（红色系）
  - 变更项 `--cpq-color-diff-changed`（黄色系）
- **底部**：方案总价对比，大字显示
- 行 hover 时两列同时高亮

#### 关键 CSS

```css
.cpq-compare {
  display: grid;
  grid-template-columns: 1fr 48px 1fr;  /* A | divider | B */
  gap: 0;
  background: var(--cpq-bg-card);
  border: 1px solid var(--cpq-border-card);
  border-radius: 12px;
  overflow: hidden;
  margin: var(--cpq-space-3) 0;
}

.cpq-compare__header-title {
  padding: var(--cpq-space-4);
  font-size: var(--el-font-size-medium);
  font-weight: var(--cpq-font-weight-semibold);
  color: var(--el-text-color-primary);
  text-align: center;
  border-bottom: 1px solid var(--el-border-color);
  grid-column: 1 / -1;
}

/* 差异高亮行 */
.cpq-compare__row--diff-added .cpq-compare__cell {
  background: rgba(5, 150, 105, 0.06);
  border-left: 3px solid var(--cpq-color-diff-added);
}

.cpq-compare__row--diff-removed .cpq-compare__cell {
  background: rgba(220, 38, 38, 0.06);
  border-left: 3px solid var(--cpq-color-diff-removed);
}

.cpq-compare__row--diff-changed .cpq-compare__cell {
  background: rgba(217, 119, 6, 0.06);
  border-left: 3px solid var(--cpq-color-diff-changed);
}

.cpq-compare__cell {
  padding: var(--cpq-space-3) var(--cpq-space-4);
  font-size: var(--el-font-size-base);
  border-bottom: 1px solid var(--el-border-color-lighter);
  transition: background var(--el-transition-duration-fast);
}

.cpq-compare__row:hover .cpq-compare__cell {
  background: var(--cpq-bg-card-hover);
}

/* 价格大字对比 */
.cpq-compare__price {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 1fr 48px 1fr;
  padding: var(--cpq-space-6);
  background: var(--el-fill-color);
}

.cpq-compare__price-value {
  font-size: var(--cpq-font-size-3xl);
  font-weight: var(--cpq-font-weight-bold);
  color: var(--cpq-color-price-primary);
  text-align: center;
}

.cpq-compare__price-value--advantage {
  color: var(--el-color-success);
}
```


### 5.5 报价确认卡片（Quote Confirmation Card）

#### 视觉描述

- **大数字**：报价总金额 `--cpq-font-size-3xl`（30px），`--cpq-font-weight-bold`（700）
- **明细行**：物料数 + 总数量 + 交货期 + 有效期等信息
- **操作区**：
  - 主操作：「确认报价」（`el-button--primary`, large size）
  - 次操作：「调整方案」（`el-button--default`）+ 「返回修改」（`el-button--text`）
- **分隔线**：总金额与明细之间 `--cpq-border-divider`
- 卡片宽度建议 400-500px，居中显示

#### 关键 CSS

```css
.cpq-quote-card {
  background: var(--cpq-bg-card);
  border: 1px solid var(--cpq-border-card);
  border-radius: 16px;
  box-shadow: var(--cpq-shadow-card);
  padding: var(--cpq-space-6);
  margin: var(--cpq-space-4) 0;
  max-width: 500px;
}

.cpq-quote-card__amount {
  text-align: center;
  margin-bottom: var(--cpq-space-4);
}

.cpq-quote-card__amount-label {
  font-size: var(--el-font-size-small);
  color: var(--el-text-color-secondary);
  margin-bottom: var(--cpq-space-2);
}

.cpq-quote-card__amount-value {
  font-size: var(--cpq-font-size-3xl);
  font-weight: var(--cpq-font-weight-bold);
  color: var(--cpq-color-price-primary);
  line-height: 1.2;
}

.cpq-quote-card__amount-currency {
  font-size: var(--el-font-size-large);
  font-weight: var(--el-font-weight-primary);
  color: var(--el-text-color-secondary);
  margin-left: var(--cpq-space-2);
}

.cpq-quote-card__divider {
  height: 1px;
  background: var(--cpq-border-divider);
  margin: var(--cpq-space-4) 0;
}

.cpq-quote-card__details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--cpq-space-3);
  margin-bottom: var(--cpq-space-6);
}

.cpq-quote-card__detail-item {
  text-align: center;
}

.cpq-quote-card__detail-label {
  font-size: var(--el-font-size-extra-small);
  color: var(--el-text-color-secondary);
}

.cpq-quote-card__detail-value {
  font-size: var(--el-font-size-base);
  font-weight: var(--cpq-font-weight-semibold);
  color: var(--el-text-color-primary);
}

.cpq-quote-card__actions {
  display: flex;
  gap: var(--cpq-space-3);
  justify-content: center;
  align-items: center;
}

.cpq-quote-card__actions .el-button--primary {
  --el-button-size: 40px;
  padding: 0 32px;
  font-size: var(--el-font-size-base);
  font-weight: 600;
}
```


### 5.6 设置面板（Settings Panel）

#### 视觉描述

- 使用 Element Plus `el-tabs`，左侧标签式（`tab-position="left"`）
- **Tab 标签**：通用 | 模型 | 报价规则 | 显示 | 关于
- 每个 tab 内容为 `el-form`，`label-position="top"`（标签在上方）
- 表单控件使用 Element Plus 默认尺寸（`size="default"`，32px 高度）
- 底部操作栏固定：「保存」+「取消」
- 面板宽度建议 600-700px

#### 关键 CSS

```css
.cpq-settings {
  background: var(--cpq-bg-card);
  border-radius: 12px;
  min-height: 400px;
}

.cpq-settings .el-tabs {
  --el-tabs-header-width: 160px;
}

.cpq-settings .el-tabs__item {
  font-size: var(--el-font-size-base);
  padding: var(--cpq-space-3) var(--cpq-space-4);
  height: auto;
  line-height: 1.5;
  border-radius: 6px;
  margin: 2px 8px;
  transition: all var(--el-transition-duration-fast);
}

.cpq-settings .el-tabs__item.is-active {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  font-weight: var(--cpq-font-weight-semibold);
}

.cpq-settings .el-form-item {
  margin-bottom: var(--cpq-space-5);
}

.cpq-settings .el-form-item__label {
  font-size: var(--el-font-size-small);
  color: var(--el-text-color-secondary);
  margin-bottom: var(--cpq-space-2);
}
```


### 5.7 侧边栏（Sidebar）

#### 视觉描述

- 左侧固定 280px，背景 `--cpq-bg-sidebar`
- **顶部**：App Logo + 名称
- **「新建对话」按钮**：`el-button--primary` full-width，上方有间距
- **会话列表**：
  - 每项：会话标题（单行截断）+ 时间戳（小字）
  - 活跃会话：左边 3px `--el-color-primary` 实色条
  - hover：背景 `--el-fill-color` 微亮
- **底部**：用户信息 / 设置入口

#### 关键 CSS

```css
.cpq-sidebar {
  width: var(--cpq-sidebar-width);
  height: 100vh;
  background: var(--cpq-bg-sidebar);
  border-right: 1px solid var(--el-border-color-light);
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;
}

.cpq-sidebar__header {
  padding: var(--cpq-space-6) var(--cpq-space-4) var(--cpq-space-4);
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.cpq-sidebar__logo {
  display: flex;
  align-items: center;
  gap: var(--cpq-space-3);
  font-size: var(--el-font-size-large);
  font-weight: var(--cpq-font-weight-semibold);
  color: var(--el-text-color-primary);
}

.cpq-sidebar__new-chat {
  margin: var(--cpq-space-4);
}

.cpq-sidebar__new-chat .el-button {
  width: 100%;
  border-radius: 8px;
}

.cpq-sidebar__conversations {
  flex: 1;
  overflow-y: auto;
  padding: var(--cpq-space-2) 0;
}

.cpq-conversation-item {
  padding: var(--cpq-space-3) var(--cpq-space-4);
  cursor: pointer;
  border-left: 3px solid transparent;
  transition: all var(--el-transition-duration-fast);
}

.cpq-conversation-item:hover {
  background: var(--el-fill-color);
}

.cpq-conversation-item--active {
  border-left-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.cpq-conversation-item__title {
  font-size: var(--el-font-size-base);
  color: var(--el-text-color-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
}

.cpq-conversation-item__time {
  font-size: var(--el-font-size-extra-small);
  color: var(--el-text-color-placeholder);
}

.cpq-sidebar__footer {
  padding: var(--cpq-space-3) var(--cpq-space-4);
  border-top: 1px solid var(--el-border-color-lighter);
}
```


### 5.8 加载状态（Loading States）

#### 骨架屏（Skeleton）

```css
/* 消息骨架屏 */
.cpq-skeleton-message {
  display: flex;
  gap: var(--cpq-space-3);
  margin-bottom: var(--cpq-space-4);
  animation: skeletonPulse 1.5s ease-in-out infinite;
}

.cpq-skeleton-message__avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--el-fill-color-dark);
  flex-shrink: 0;
}

.cpq-skeleton-message__content {
  flex: 1;
}

.cpq-skeleton-message__line {
  height: 14px;
  border-radius: 4px;
  background: var(--el-fill-color-dark);
  margin-bottom: var(--cpq-space-2);
}

.cpq-skeleton-message__line:last-child {
  width: 60%;
}

/* 产品卡片骨架屏 */
.cpq-skeleton-card {
  height: 380px;
  border-radius: 12px;
  background: var(--el-fill-color);
  animation: skeletonPulse 1.5s ease-in-out infinite;
}

@keyframes skeletonPulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

/* 流式打字机光标 */
.cpq-typing-cursor {
  display: inline-block;
  width: 2px;
  height: 1.1em;
  background: var(--el-color-primary);
  margin-left: 2px;
  vertical-align: text-bottom;
  animation: cursorBlink 1s step-end infinite;
}

@keyframes cursorBlink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* 脉冲加载动画 */
.cpq-loading-pulse {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: var(--el-font-size-small);
  color: var(--el-text-color-secondary);
}

.cpq-loading-pulse__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--el-color-primary);
  animation: dotBounce 1.4s ease-in-out infinite both;
}

.cpq-loading-pulse__dot:nth-child(1) { animation-delay: -0.32s; }
.cpq-loading-pulse__dot:nth-child(2) { animation-delay: -0.16s; }
.cpq-loading-pulse__dot:nth-child(3) { animation-delay: 0s; }

@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
```


---

## 6. 关键状态视觉处理（Key States）

| 状态 | 视觉表现 | 适用组件 |
|------|----------|----------|
| **空态** (Empty) | 居中提示图标（80×80px 浅色 icon）+ 引导文字 + 「开始新配置」按钮 | 会话列表无历史、产品推荐无结果 |
| **加载** (Loading) | 骨架屏（消息/卡片）+ 思考过程脉冲点 + 流式打字机光标 | 首次加载、AI 思考中、流式输出 |
| **错误** (Error) | 红色 `--el-color-error` 边框 + 背景 + error icon + 重试按钮 | 网络异常、API 超时、配置不可行 |
| **成功** (Success) | 绿色 `--el-color-success` 图标 + 提示 + 确认对话框 | 报价确认完成、配置保存成功 |
| **禁用** (Disabled) | 0.6 不透明度 + `cursor: not-allowed` + 去色效果 | 不可选产品、已确认报价 |

### 空态视觉示例

```css
.cpq-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--cpq-space-12) var(--cpq-space-6);
  text-align: center;
}

.cpq-empty-state__icon {
  width: 80px;
  height: 80px;
  opacity: 0.3;
  margin-bottom: var(--cpq-space-6);
  color: var(--el-text-color-placeholder);
}

.cpq-empty-state__title {
  font-size: var(--el-font-size-medium);
  font-weight: var(--cpq-font-weight-semibold);
  color: var(--el-text-color-secondary);
  margin-bottom: var(--cpq-space-2);
}

.cpq-empty-state__desc {
  font-size: var(--el-font-size-base);
  color: var(--el-text-color-placeholder);
  margin-bottom: var(--cpq-space-6);
  max-width: 300px;
}
```

### 错误状态视觉示例

```css
.cpq-error-state {
  display: flex;
  align-items: flex-start;
  gap: var(--cpq-space-3);
  padding: var(--cpq-space-4);
  background: var(--el-color-error-light-9);
  border: 1px solid var(--el-color-error-light-5);
  border-radius: 8px;
  margin: var(--cpq-space-3) 0;
}

.cpq-error-state__icon {
  color: var(--el-color-error);
  font-size: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.cpq-error-state__message {
  flex: 1;
  font-size: var(--el-font-size-base);
  color: var(--el-text-color-primary);
}

.cpq-error-state__retry {
  flex-shrink: 0;
}
```


---

## 7. 交互动效规范（Animation & Motion）

### 7.1 动效曲线（Easing Curves）

```css
:root {
  --el-transition-function-ease-in-out-bezier: cubic-bezier(0.645, 0.045, 0.355, 1);

  --cpq-ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --cpq-ease-in-out-quart: cubic-bezier(0.76, 0, 0.24, 1);
  --cpq-ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  --cpq-ease-linear: cubic-bezier(0, 0, 1, 1);
}
```

### 7.2 持续时间（Duration）

```css
:root {
  --el-transition-duration: 0.3s;
  --el-transition-duration-fast: 0.2s;
  --cpq-duration-instant: 0.1s;
  --cpq-duration-normal: 0.3s;
  --cpq-duration-slow: 0.5s;
  --cpq-duration-typing: 0.05s;
}
```

### 7.3 动画规范表

| 动画 | 属性 | 时长 | 曲线 | 延迟 |
|------|------|------|------|------|
| **消息滑入**（用户） | translateX(20px) + opacity | 0.3s | ease-out-expo | 0 |
| **消息滑入**（Agent） | translateX(-20px) + opacity | 0.3s | ease-out-expo | 0.1s |
| **打字机光标** | opacity 闪烁 | 1s/cycle | step-end | 0 |
| **卡片 hover** | translateY(-2px) + shadow | 0.2s | ease-in-out | 0 |
| **卡片入场** | translateY(10px) + opacity | 0.35s | ease-out-expo | 0.1s * index |
| **骨架屏脉冲** | opacity 变化 | 1.5s | ease-in-out | 0 |
| **页面过渡** | opacity | 0.3s | in-out-quart | 0 |
| **按钮点击** | scale(0.97) | 0.1s | spring | 0 |
| **侧边栏展开** | width + opacity | 0.3s | in-out-quart | 0 |
| **模态框弹出** | scale(0.9→1) + opacity | 0.25s | ease-out-expo | 0 |

### 7.4 关键帧动画定义

```css
@keyframes messageSlideIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.cpq-product-card {
  animation: cardEntrance 0.35s var(--cpq-ease-out-expo) both;
}
.cpq-product-card:nth-child(1) { animation-delay: 0.05s; }
.cpq-product-card:nth-child(2) { animation-delay: 0.15s; }
.cpq-product-card:nth-child(3) { animation-delay: 0.25s; }

@keyframes cardEntrance {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes modalZoomIn {
  from { opacity: 0; transform: scale(0.92); }
  to { opacity: 1; transform: scale(1); }
}
```


---

## 8. 主题适配速查表（Theme Mapping）

| CSS 变量 | 亮色 | 暗色 | 影响组件 |
|----------|------|------|----------|
| `--el-bg-color` | `#ffffff` | `#0f172a` | 整体应用背景 |
| `--el-bg-color-page` | `#f0f2f5` | `#0a0f1e` | 页面二级背景 |
| `--el-bg-color-overlay` | `#ffffff` | `#1a2332` | 弹窗、下拉菜单 |
| `--cpq-bg-chat` | `#f8fafc` | `#0d1425` | 聊天区域 |
| `--cpq-bg-sidebar` | `#f1f5f9` | `#0a0f1e` | 侧边栏 |
| `--cpq-bg-card` | `#ffffff` | `#162032` | 产品卡片、报价卡片 |
| `--cpq-bg-message-user` | `#dbeafe` | `#1e3a8a` | 用户消息气泡 |
| `--cpq-bg-message-agent` | `#ffffff` | `#1a2332` | Agent 消息气泡 |
| `--el-text-color-primary` | `#111827` | `#f9fafb` | 主要文字 |
| `--el-text-color-regular` | `#374151` | `#d1d5db` | 正文文字 |
| `--el-text-color-secondary` | `#6b7280` | `#9ca3af` | 辅助文字 |
| `--el-border-color` | `#d1d5db` | `#374151` | 默认边框 |
| `--cpq-color-match-high` | `#059669` | `#34d399` | 高匹配度标签 |
| `--cpq-color-match-medium` | `#d97706` | `#fbbf24` | 中匹配度标签 |
| `--cpq-color-match-low` | `#dc2626` | `#f87171` | 低匹配度标签 |

**主题切换实现**：

```ts
// composables/useTheme.ts
import { useStorage } from '@vueuse/core'

function useTheme() {
  const isDark = useStorage('cpq-theme', false)

  watch(isDark, (val) => {
    document.documentElement.setAttribute('data-theme', val ? 'dark' : 'light')
    document.documentElement.classList.toggle('dark', val)
  }, { immediate: true })

  return { isDark }
}
```

> 注意：需同步启用 Element Plus 的 `dark` class 以应用其内置暗色变量。


---

## 9. Element Plus 组件覆盖指南

| Element Plus 组件 | 覆盖方式 | 说明 |
|------------------|----------|------|
| `el-button` | `--el-button-bg-color` 等 CSS 变量 | 统一主色；large 用于报价确认等行动点 |
| `el-table` | 定制 `--el-table-*` 变量 + CPQ 样式类 | BOM 表格使用自定义样式 |
| `el-tabs` | `--el-tabs-*` 变量 | 设置面板使用左侧 tab |
| `el-card` | 不使用（自定义 `.cpq-product-card`） | 产品/报价卡片自定义，灵活度更高 |
| `el-skeleton` | 部分使用 + 自定义 CSS | 消息骨架屏、产品卡片骨架屏自定义 |
| `el-tag` | `--el-tag-*` 变量 | 匹配度标签使用自定义 class |
| `el-dialog` | `--el-dialog-*` 变量 | 模态框弹窗 |
| `el-form` | `label-position="top"` | 设置面板配置表单 |
| `el-input` | `--el-input-*` 变量 | 搜索栏、聊天输入框 |
| `el-checkbox` | 默认 + 覆盖 | 设置面板多选配置项 |
| `el-radio` | 默认 + 覆盖 | 方案选择等单选项 |


---

## 10. 全局 CSS 注入顺序

```scss
// 1. styles/variables/cpq-tokens.scss
//    基础设计令牌：spacing, font, shadow custom vars
//    亮色 CSS 变量 + 暗色 CSS 变量

// 2. styles/variables/element-overrides.scss
//    Element Plus 主题覆盖（SCSS 变量方式）

// 3. styles/global.scss
//    全局基础样式重置
//    消息气泡、产品卡片等全局组件样式
//    动画、关键帧定义
//    暗色主题下的组件适配覆盖
```

**入口配置**：

```ts
// src/main.ts
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import './styles/global.scss'
import App from './App.vue'

const app = createApp(App)
app.use(ElementPlus)
app.mount('#app')
```

---

> **文档编制**：用户界面视觉设计师
> **日期**：2026-07-05
> **配套资源**：亮色/暗色 CSS 变量文件（cpq-tokens.scss）、组件库脚手架、Figma 组件库（另见）
