import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { sseChat, fetchSessions, fetchSession, deleteSession as apiDeleteSession } from '../api/agent'
import type { Message, Session, SessionItem } from '../types'

// 简易 UUID 生成（避免引入 uuid 包）
function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 10)
}

export const useChatStore = defineStore('chat', () => {
  // 当前会话
  const currentSession = ref<Session>({
    id: generateId(),
    title: '新对话',
    messages: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  })

  // 会话列表
  const sessions = ref<SessionItem[]>([])

  // 是否正在接收流式响应
  const isStreaming = ref(false)

  // 加载状态
  const loading = ref(false)

  // 会话列表加载状态
  const sessionsLoading = ref(false)

  // 错误信息
  const error = ref<string | null>(null)

  // 用户消息列表（展平）
  const messages = computed(() => currentSession.value.messages)

  /**
   * 加载会话列表
   */
  async function loadSessions() {
    sessionsLoading.value = true
    try {
      sessions.value = await fetchSessions()
    } catch (err) {
      console.warn('无法加载会话列表:', err)
      // 使用空列表
      sessions.value = []
    } finally {
      sessionsLoading.value = false
    }
  }

  /**
   * 创建新会话
   */
  function newSession() {
    currentSession.value = {
      id: generateId(),
      title: '新对话',
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    error.value = null
  }

  /**
   * 切换到指定会话
   */
  async function switchSession(sessionId: string) {
    if (sessionId === currentSession.value.id) return

    loading.value = true
    try {
      const sessionData = await fetchSession(sessionId)
      currentSession.value = {
        id: sessionData.id,
        title: sessionData.title,
        messages: sessionData.messages.map((m) => ({
          ...m,
          status: 'done' as Message['status'],
        })),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }
    } catch (err) {
      console.error('加载会话失败:', err)
      error.value = '加载会话失败'
    } finally {
      loading.value = false
    }
  }

  /**
   * 添加消息到当前会话
   */
  function addMessage(
    role: Message['role'],
    content: string,
    status: Message['status'] = 'done'
  ): Message {
    const msg: Message = {
      id: generateId(),
      role,
      content,
      status,
      createdAt: new Date().toISOString(),
    }
    currentSession.value.messages.push(msg)
    currentSession.value.updatedAt = new Date().toISOString()

    // 如果是第一条用户消息，用内容做会话标题
    if (
      role === 'user' &&
      currentSession.value.messages.filter((m) => m.role === 'user').length === 1
    ) {
      currentSession.value.title =
        content.slice(0, 30) + (content.length > 30 ? '...' : '')
    }

    return msg
  }

  /**
   * 更新最后一条助手消息
   */
  function updateLastAssistant(
    content: string,
    status: Message['status'] = 'streaming'
  ) {
    const msgs = currentSession.value.messages
    if (msgs.length > 0 && msgs[msgs.length - 1].role === 'assistant') {
      msgs[msgs.length - 1].content = content
      msgs[msgs.length - 1].status = status
    }
  }

  /**
   * 发送消息 - 连接后端 SSE
   */
  async function sendMessage(text: string) {
    if (!text.trim() || isStreaming.value) return

    error.value = null

    // 添加用户消息
    addMessage('user', text.trim(), 'done')

    // 添加空的助手消息（流式填充）
    const assistantIdx = currentSession.value.messages.length
    addMessage('assistant', '', 'streaming')
    isStreaming.value = true
    
    // 获取 reactive 包装后的消息引用
    function getAssistant() {
      return currentSession.value.messages[assistantIdx]
    }

    try {
      const abortController = new AbortController()

      // 带重连的 SSE 通信
      const generator = sseChat(
        currentSession.value.messages.map((m) => ({
          ...m,
          status: 'done' as Message['status'],
        })),
        abortController.signal
      )

      for await (const event of generator) {
        if (event.type === 'message_delta') {
          const msg = getAssistant()
          msg.content = msg.content + event.data
          msg.status = 'streaming'
        } else if (event.type === 'status') {
          // 显示处理步骤，去重：相同 label 不重复添加
          const data = event.data || {}
          const status = typeof data === 'string' ? data : data.status
          let label = status
          
          if (status === 'processing') {
            label = '正在分析您的需求...'
          } else if (status === 'tool_call') {
            const toolMap: Record<string, string> = {
              search_product: '正在搜索产品...',
              get_model_detail: '正在加载产品详情...',
              validate_configuration: '正在验证配置规则...',
              get_bom: '正在生成 BOM 清单...',
              get_pricing: '正在计算定价...',
              search_customers: '正在查找客户...',
              create_quote: '正在生成报价单...',
              reverse_match_price: '正在反向匹配价格...',
              compare_solutions: '正在对比方案...',
            }
            const tool = data.tool || ''
            label = toolMap[tool] || `正在调取数据...`
          } else if (status === 'tool_result') {
            continue
          } else if (status === 'error') {
            const msg = getAssistant()
            currentSession.value.messages = currentSession.value.messages.filter(
              (m) => m.role !== 'thinking'
            )
            const errMsg = data.message || data.error || '未知错误'
            msg.content = errMsg
            msg.status = 'error'
            error.value = errMsg
            break
          }
          
          // 去重：检查上一条消息是否相同
          const msgs = currentSession.value.messages
          const lastMsg = msgs[msgs.length - 1]
          if (lastMsg && lastMsg.role === 'thinking' && lastMsg.content === label) {
            // 跳过重复
          } else {
            addMessage('thinking', label, 'thinking')
          }
        } else if (event.type === 'done') {
          const assistant = getAssistant()
          if (assistant.status !== 'error') {
            currentSession.value.messages = currentSession.value.messages.filter(
              (m) => m.role !== 'thinking'
            )
            assistant.status = 'done'
          }
          break
        } else if (event.type === 'error') {
          const msg = getAssistant()
          currentSession.value.messages = currentSession.value.messages.filter(
            (m) => m.role !== 'thinking'
          )
          msg.content = event.data
          msg.status = 'error'
          error.value = event.data
          break
        }
      }
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : String(err)
      updateLastAssistant(errMsg, 'error')
      error.value = errMsg
    } finally {
      isStreaming.value = false
    }
  }

  /**
   * 删除会话
   */
  async function removeSession(sessionId: string) {
    try {
      await apiDeleteSession(sessionId)
      sessions.value = sessions.value.filter((s) => s.id !== sessionId)
      if (currentSession.value.id === sessionId) {
        newSession()
      }
    } catch (err) {
      console.error('删除会话失败:', err)
      throw err
    }
  }

  return {
    currentSession,
    sessions,
    isStreaming,
    loading,
    sessionsLoading,
    error,
    messages,
    loadSessions,
    newSession,
    switchSession,
    sendMessage,
    removeSession,
  }
})
