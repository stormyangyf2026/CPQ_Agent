import type { Message, SSEEvent, SSEEventType } from '../types'

// 自动检测运行环境：Electron 包装版 vs 浏览器开发模式
declare global {
  interface Window {
    electronAPI?: {
      getBackendUrl: () => Promise<string>
      getBackendStatus: () => Promise<{
        running: boolean
        error: string | null
        port: number
        pythonFound: string
        backendDir: string
        configPath: string
      }>
    }
    __CPQ_BACKEND_URL__?: string
  }
}

// Electron 环境下通过 preload 注入的全局变量获取后端地址（同步，避免竞态）
let BASE_URL: string
if (typeof window !== 'undefined' && window.__CPQ_BACKEND_URL__) {
  BASE_URL = window.__CPQ_BACKEND_URL__
} else if (typeof window !== 'undefined' && window.electronAPI) {
  // 兜底：异步获取（可能在首次请求时尚未就绪）
  BASE_URL = 'http://127.0.0.1:58118'  // Electron 生产模式的默认端口
  window.electronAPI.getBackendUrl().then((url) => {
    BASE_URL = url
  })
} else {
  BASE_URL = 'http://localhost:58100'  // 浏览器开发模式
}

/**
 * 默认的指数退避重连参数
 */
const MAX_RETRIES = 5
const BASE_DELAY_MS = 1000

/**
 * 将消息历史转换为 API 请求格式
 */
function messagesToPayload(messages: Message[]) {
  return messages.map((m) => ({
    role: m.role,
    content: m.content,
  }))
}

/**
 * SSE 聊天 - 使用 fetch + ReadableStream 实现流式通信
 * 支持断线重连（指数退避）
 */
export async function* sseChat(
  messages: Message[],
  signal?: AbortSignal
): AsyncGenerator<SSEEvent> {
  let retryCount = 0
  let lastError: Error | null = null

  while (retryCount <= MAX_RETRIES) {
    try {
      const response = await fetch(`${BASE_URL}/agent/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'text/event-stream',
        },
        body: JSON.stringify({
          messages: messagesToPayload(messages),
        }),
        signal,
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const contentType = response.headers.get('content-type') || ''
      if (!contentType.includes('text/event-stream')) {
        // 如果不是 SSE，读取完整响应
        const text = await response.text()
        yield {
          type: 'message_delta' as SSEEventType,
          data: text,
        }
        yield {
          type: 'done' as SSEEventType,
          data: '',
        }
        return
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('Response body is not readable')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // 按 SSE 协议解析：每个事件以 \n\n 分隔
        const lines = buffer.split('\n')
        // 保留最后一段（可能不完整）
        buffer = lines.pop() || ''

        let currentEventType: SSEEventType = 'message_delta'
        let currentData = ''

        for (const line of lines) {
          if (line.startsWith('event:')) {
            const eventName = line.slice(6).trim() as SSEEventType
            if (
              eventName === 'message_delta' ||
              eventName === 'status' ||
              eventName === 'done' ||
              eventName === 'error'
            ) {
              currentEventType = eventName
            }
          } else if (line.startsWith('data:')) {
            currentData = line.slice(5).trim()

            if (currentData === '[DONE]') {
              yield { type: 'done', data: '' }
              return
            }

            // 尝试解析 JSON
            if (currentData.startsWith('{') || currentData.startsWith('[')) {
              try {
                const parsed = JSON.parse(currentData)
                // 使用 SSE event: 字段优先确定类型
                if (currentEventType === 'done') {
                  yield { type: 'done', data: parsed.content || '' }
                } else if (currentEventType === 'status') {
                  yield { type: 'status', data: parsed }
                } else if (parsed.error) {
                  yield { type: 'error', data: parsed.error }
                } else if (parsed.content && currentEventType === 'message_delta') {
                  yield { type: 'message_delta', data: parsed.content }
                } else {
                  yield { type: currentEventType, data: currentData }
                }
              } catch {
                yield { type: currentEventType, data: currentData }
              }
            } else {
              yield { type: currentEventType, data: currentData }
            }
          } else if (line.startsWith(':')) {
            // 注释行，忽略
            continue
          }
        }
      }

      // 处理残留 buffer
      if (buffer.trim()) {
        yield { type: 'message_delta', data: buffer }
      }

      // 正常完成
      yield { type: 'done', data: '' }
      return
    } catch (err) {
      if (signal?.aborted) {
        yield { type: 'error', data: '请求已取消' }
        return
      }

      lastError = err instanceof Error ? err : new Error(String(err))
      retryCount++

      if (retryCount > MAX_RETRIES) {
        yield {
          type: 'error',
          data: `连接失败: ${lastError.message}（已重试 ${MAX_RETRIES} 次）`,
        }
        return
      }

      // 指数退避
      const delay = BASE_DELAY_MS * Math.pow(2, retryCount - 1) + Math.random() * 1000
      yield {
        type: 'status',
        data: `连接断开，${Math.round(delay / 1000)} 秒后自动重连（第 ${retryCount} 次）`,
      }

      await new Promise((resolve) => setTimeout(resolve, delay))
    }
  }
}

/**
 * 加载会话历史列表
 */
export async function fetchSessions(): Promise<
  { id: string; title: string; updatedAt: string; messageCount: number }[]
> {
  const response = await fetch(`${BASE_URL}/sessions`)
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
  return response.json()
}

/**
 * 加载单个会话详情
 */
export async function fetchSession(
  sessionId: string
): Promise<{ id: string; title: string; messages: Message[] }> {
  const response = await fetch(`${BASE_URL}/sessions/${sessionId}`)
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
  return response.json()
}

/**
 * 删除会话
 */
export async function deleteSession(sessionId: string): Promise<void> {
  const response = await fetch(`${BASE_URL}/sessions/${sessionId}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
}

/**
 * 加载配置
 */
export async function fetchConfig(): Promise<Record<string, any>> {
  const response = await fetch(`${BASE_URL}/config`)
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
  return response.json()
}

/**
 * 更新配置
 */
export async function updateConfig(
  config: Record<string, any>
): Promise<Record<string, any>> {
  const response = await fetch(`${BASE_URL}/config`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(config),
  })
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
  return response.json()
}

/**
 * 获取后端诊断状态（仅 Electron 环境可用）
 */
export async function getBackendStatus():
  Promise<{ running: boolean; error: string | null; port: number; pythonFound: string; backendDir: string; configPath: string } | null> {
  try {
    if (typeof window !== 'undefined' && window.electronAPI) {
      return await window.electronAPI.getBackendStatus()
    }
    return null
  } catch {
    return null
  }
}

/**
 * 测试连接
 */
export async function testConnection(): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(`${BASE_URL}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000),
    })
    if (response.ok) {
      return { success: true, message: '连接成功' }
    }
    return { success: false, message: `服务器返回状态码 ${response.status}` }
  } catch (err) {
    return {
      success: false,
      message: `连接失败: ${err instanceof Error ? err.message : String(err)}`,
    }
  }
}
