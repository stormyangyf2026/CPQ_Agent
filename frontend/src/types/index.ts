// 消息角色
export type MessageRole = 'user' | 'assistant' | 'system' | 'thinking'

// 消息状态
export type MessageStatus = 'sending' | 'streaming' | 'done' | 'error' | 'thinking'

// 消息中的内容块
export interface ContentPart {
  type: 'text' | 'thinking'
  text: string
}

// 聊天消息
export interface Message {
  id: string
  role: MessageRole
  content: string
  contentParts?: ContentPart[]
  status: MessageStatus
  createdAt: string
}

// 会话
export interface Session {
  id: string
  title: string
  messages: Message[]
  createdAt: string
  updatedAt: string
}

// SSE 事件类型
export type SSEEventType = 'message_delta' | 'status' | 'done' | 'error'

// SSE 事件
export interface SSEEvent {
  type: SSEEventType
  data: string
  sessionId?: string
}

// 配置分类
export type ConfigCategory = 'model' | 'cpq' | 'agent' | 'ui' | 'system'

// 配置项定义
export interface ConfigItem {
  key: string
  label: string
  type: 'select' | 'input' | 'password' | 'toggle' | 'number'
  category: ConfigCategory
  value: string | number | boolean
  options?: { label: string; value: string | number }[]
  placeholder?: string
  description?: string
}

// 应用配置
export interface AppConfig {
  model: ConfigItem[]
  cpq: ConfigItem[]
  agent: ConfigItem[]
  ui: ConfigItem[]
  system: ConfigItem[]
}

// 侧边栏会话项
export interface SessionItem {
  id: string
  title: string
  updatedAt: string
  messageCount: number
}
