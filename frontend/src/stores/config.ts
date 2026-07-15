import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { fetchConfig, updateConfig as apiUpdateConfig } from '../api/agent'
import type { ConfigItem, ConfigCategory } from '../types'

function getDefaultConfig(): Record<ConfigCategory, ConfigItem[]> {
  return {
    model: [
      { key: 'model_provider', label: '模型提供商', type: 'select', category: 'model', value: 'deepseek', options: [{ label: 'DeepSeek (推荐)', value: 'deepseek' }, { label: 'OpenAI', value: 'openai' }, { label: 'Anthropic', value: 'anthropic' }, { label: 'Ollama (本地)', value: 'ollama' }], description: '选择 AI 模型服务提供商' },
      { key: 'model_name', label: '模型名称', type: 'select', category: 'model', value: 'deepseek-v4-pro', options: [{ label: 'DeepSeek V4 Pro', value: 'deepseek-v4-pro' }, { label: 'DeepSeek V4 Flash', value: 'deepseek-v4-flash' }], description: '使用的 AI 模型' },
      { key: 'model_base_url', label: 'Base URL', type: 'input', category: 'model', value: 'https://api.deepseek.com', placeholder: 'https://api.deepseek.com', description: 'API 端点地址' },
      { key: 'model_temperature', label: '温度 (Temperature)', type: 'number', category: 'model', value: 0.7, description: '控制输出的随机性' },
      { key: 'model_max_tokens', label: '最大 Token 数', type: 'number', category: 'model', value: 4096, description: '每次回复的最大 token 数量' },
    ],
    cpq: [
      { key: 'cpq_api_url', label: 'CPQ 地址', type: 'input', category: 'cpq', value: 'http://localhost:30000', placeholder: 'http://localhost:30000', description: 'CPQ App 后端地址' },
      { key: 'cpq_client_id', label: 'Client ID', type: 'input', category: 'cpq', value: 'e5cd7e4891bf95d1d19206ce24a7b32e', placeholder: 'OAuth2 Client ID', description: 'CPQ 的 OAuth2 客户端' },
      { key: 'cpq_username', label: '用户名', type: 'input', category: 'cpq', value: 'admin', placeholder: 'admin', description: 'CPQ 登录用户名' },
      { key: 'cpq_password', label: '密码', type: 'password', category: 'cpq', value: '', placeholder: 'CPQ 登录密码', description: '用于获取 Access Token' },
      { key: 'cpq_timeout', label: '超时时间 (秒)', type: 'number', category: 'cpq', value: 30, description: 'CPQ 请求超时时间' },
    ],
    agent: [
      { key: 'agent_auto_suggest', label: '自动建议', type: 'toggle', category: 'agent', value: true, description: 'Agent 是否自动提供配置建议' },
      { key: 'agent_verbose', label: '详细输出', type: 'toggle', category: 'agent', value: false, description: '是否显示 Agent 思考过程的详细信息' },
      { key: 'agent_max_iterations', label: '最大迭代次数', type: 'number', category: 'agent', value: 10, description: 'Agent 单次任务的最大工具调用次数' },
    ],
    ui: [
      { key: 'ui_theme', label: '主题', type: 'select', category: 'ui', value: 'light', options: [{ label: '浅色', value: 'light' }, { label: '深色', value: 'dark' }, { label: '跟随系统', value: 'system' }], description: '界面主题' },
      { key: 'ui_font_size', label: '字体大小', type: 'select', category: 'ui', value: 'medium', options: [{ label: '小', value: 'small' }, { label: '中', value: 'medium' }, { label: '大', value: 'large' }], description: '聊天区域字体大小' },
      { key: 'ui_send_on_enter', label: 'Enter 发送', type: 'toggle', category: 'ui', value: true, description: '按 Enter 键发送消息' },
      { key: 'ui_timestamp', label: '显示时间戳', type: 'toggle', category: 'ui', value: true, description: '在消息旁显示时间' },
    ],
    system: [
      { key: 'system_language', label: '语言', type: 'select', category: 'system', value: 'zh-CN', options: [{ label: '中文', value: 'zh-CN' }, { label: 'English', value: 'en-US' }, { label: '日本語', value: 'ja-JP' }], description: '系统界面语言' },
      { key: 'system_log_level', label: '日志级别', type: 'select', category: 'system', value: 'info', options: [{ label: 'Debug', value: 'debug' }, { label: 'Info', value: 'info' }, { label: 'Warn', value: 'warn' }, { label: 'Error', value: 'error' }], description: '日志记录级别' },
      { key: 'system_auto_save', label: '自动保存', type: 'toggle', category: 'system', value: true, description: '自动保存聊天记录' },
    ],
  }
}

export const useConfigStore = defineStore('config', () => {
  const configs = reactive<Record<ConfigCategory, ConfigItem[]>>(getDefaultConfig())
  const loading = ref(false)
  const saving = ref(false)
  const loaded = ref(false)

  async function loadConfig() {
    loading.value = true
    try {
      const serverConfig = await fetchConfig()
      applyServerConfig(serverConfig)
    } catch (err) {
      // 后端不可达，尝试从 localStorage 恢复
      console.warn('无法加载后端配置:', err)
      try {
        const saved = localStorage.getItem('cpq-agent-config')
        if (saved) {
          const local = JSON.parse(saved)
          // 将 localStorage 的扁平 key → configs 中的值
          const flatToItemKey: Record<string, string> = {
            model_base_url: 'model_base_url',
            model_api_key: 'model_api_key',
            model_name: 'model_name',
            model_temperature: 'model_temperature',
            model_max_tokens: 'model_max_tokens',
            cpq_api_url: 'cpq_api_url',
            cpq_client_id: 'cpq_client_id',
            cpq_username: 'cpq_username',
            cpq_password: 'cpq_password',
            cpq_timeout: 'cpq_timeout',
            agent_auto_suggest: 'agent_auto_suggest',
            agent_verbose: 'agent_verbose',
            agent_max_iterations: 'agent_max_iterations',
            ui_theme: 'ui_theme',
            ui_font_size: 'ui_font_size',
            ui_send_on_enter: 'ui_send_on_enter',
            ui_timestamp: 'ui_timestamp',
            system_language: 'system_language',
            system_log_level: 'system_log_level',
            system_auto_save: 'system_auto_save',
          }
          for (const [key, val] of Object.entries(local)) {
            if (flatToItemKey[key]) updateItem(key, val)
          }
          console.log('已从本地存储恢复配置')
        }
      } catch {
        console.warn('本地存储配置恢复失败')
      }
    } finally {
      loaded.value = true
      loading.value = false
    }
  }

  function applyServerConfig(serverConfig: Record<string, any>) {
    const keyMap: Record<string, string> = {
      model_provider: "model.provider",
      model_name: "model.model_name",
      model_base_url: "model.base_url",
      model_temperature: "model.temperature",
      model_max_tokens: "model.max_tokens",
      cpq_api_url: "cpq.base_url",
      cpq_client_id: "cpq.client_id",
      cpq_username: "cpq.username",
      cpq_password: "cpq.password",
      cpq_timeout: "cpq.timeout",
      agent_auto_suggest: "agent.auto_suggest",
      agent_verbose: "agent.verbose",
      agent_max_iterations: "agent.max_iterations",
      ui_theme: "ui.theme",
      ui_font_size: "ui.font_size",
      ui_send_on_enter: "ui.send_on_enter",
      ui_timestamp: "ui.timestamp",
      system_language: "ui.language",
      system_log_level: "logging.level",
      system_auto_save: "system.auto_save",
    }
    function getNested(obj: any, path: string): any {
      return path.split(".").reduce((o, k) => (o != null ? o[k] : undefined), obj)
    }
    for (const category of Object.keys(configs) as ConfigCategory[]) {
      for (const item of configs[category]) {
        const backendPath = keyMap[item.key]
        if (backendPath) {
          const val = getNested(serverConfig, backendPath)
          if (val !== undefined) item.value = val
        }
      }
    }
  }

  function getFlatConfig(): Record<string, any> {
    const flat: Record<string, any> = {}
    for (const category of Object.keys(configs) as ConfigCategory[])
      for (const item of configs[category]) flat[item.key] = item.value
    return flat
  }

  async function saveConfig() {
    saving.value = true
    try {
      const flat = getFlatConfig()
      // 先尝试后端 API
      await apiUpdateConfig(flat)
      // 同时存 localStorage 兜底（即使后端不可达，下次加载也能用）
      try { localStorage.setItem('cpq-agent-config', JSON.stringify(flat)) } catch { /* quota exceeded 等忽略 */ }
      return true
    } catch (err) {
      // 后端不可达时，至少保存到 localStorage
      try {
        localStorage.setItem('cpq-agent-config', JSON.stringify(getFlatConfig()))
        console.warn('后端不可达，配置已保存到本地存储（重启生效）')
      } catch { /* ignore */ }
      console.error('保存配置失败:', err)
      throw err
    } finally { saving.value = false }
  }

  function getConfigsByCategory(category: ConfigCategory): ConfigItem[] {
    return configs[category] || []
  }

  function updateItem(key: string, value: string | number | boolean) {
    for (const category of Object.keys(configs) as ConfigCategory[]) {
      const item = configs[category].find((i) => i.key === key)
      if (item) { item.value = value; return }
    }
  }

  function resetToDefault() {
    const defaults = getDefaultConfig()
    for (const category of Object.keys(configs) as ConfigCategory[])
      configs[category] = defaults[category].map((item) => ({ ...item }))
  }

  return { configs, loading, saving, loaded, loadConfig, saveConfig, getConfigsByCategory, updateItem, resetToDefault, getFlatConfig }
})
