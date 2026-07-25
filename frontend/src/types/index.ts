// 消息角色
export type MessageRole = 'user' | 'assistant' | 'system' | 'thinking'

// 消息状态
export type MessageStatus = 'sending' | 'streaming' | 'done' | 'error' | 'thinking'

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
export type SSEEventType = 'message_delta' | 'status' | 'done' | 'error' | 'match_result' | 'process_confirm'

// SSE 事件
export interface SSEEvent {
  type: SSEEventType
  data: string | MatchResult | any
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

// ★ 新增：匹配结果消息类型
export interface MatchResult {
  resultId: number
  sessionId: string
  recommendations: Recommendation[]
  threshold: number
  thresholdPassed: boolean
  suggestDiy: boolean
  totalScored: number
}

export interface Recommendation {
  rank: number
  modelId: number
  modelCode: string
  modelName: string
  imageUrl?: string
  coreParams: Record<string, any>
  matchDifferences: string
  priceRange: { min: number; max: number }
  aiReason: string
  basePrice: number
  moq: number
  leadTimeDays: number
  stockQty: number
  totalScore: number
  dimensionScores: DimensionScore[]
}

export interface DimensionScore {
  dimensionCode: string
  dimensionName: string
  rawScore: number
  weight: number
  weighted: number
  detail: string
  difference: string
}

// ★ 新增：工艺确认消息类型
export interface ProcessConfirm {
  confirmId: number
  chainId?: number
  recordId?: number
  resultId: number
  modelId: number
  modelCode?: string
  modelName?: string
  requirementText?: string
  status: 'PENDING' | 'CONFIRMED' | 'REJECTED' | 'REPLACED'
  replacedModelId?: number | string
  replacedModelCode?: string
  replacedModelName?: string
  replacedReason?: string
  message: string
}

// ★ 消息内容块扩展
// ★ 报价单消息类型
export interface QuoteCreated {
  quoteId: string
  quoteNo: string
  modelCode: string
  modelName: string
  quantity: number
  unitPrice: number
  totalPrice: number
}

export interface ContentPart {
  type: 'text' | 'thinking' | 'match_result' | 'process_confirm' | 'replacement_notice' | 'quote_created'
  text?: string
  data?: MatchResult | ProcessConfirm | QuoteCreated | any
}
