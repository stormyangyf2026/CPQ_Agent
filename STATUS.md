# STATUS.md — CPQ Agent App 项目状态

> 最后更新: 2026-07-13 19:40 | 当前阶段: v1.3 修复完成

---

## 一句话状态

**Windows 安装包「保存配置失败」问题已修复。配置持久化已实现（磁盘 + localStorage 双写），端到端测试通过。**

---

## 当前进度

| 阶段 | 内容 | 状态 |
|------|------|------|
| P0 后端 | 9 tools + FastAPI + config | ✅ |
| P1 前端基础 | ChatView/Sidebar/SSE | ✅ |
| P1 前端组件 | 9 widgets + settings | ✅ |
| P2 反向匹配 | reverse_match_price | ✅ |
| P2 方案对比 | compare_solutions | ✅ |
| P3 PWA | manifest + Service Worker | ✅ |
| P3 Electron | main.cjs + preload.cjs | ✅ |
| P3 打包 | .dmg / .exe 构建 | ⏳ |
| v1.3 修复 | 配置持久化 + 错误诊断 | ✅ 2026-07-13 |

---

## v1.3 修复详情 (2026-07-13)

### 修复文件清单

| 文件 | 改动 |
|------|------|
| `backend/config.py` | 新增 `save_config()` 函数，配置写入 YAML 磁盘文件 + 原子写入（tempfile + os.replace） |
| `backend/server.py` | `update_config` 调用 `save_config()` 持久化；新增 `/health/diagnostics` 端点；支持 `cpq_timeout` 字段 |
| `frontend/electron/main.cjs` | 增加 `backendError` 变量记录错误；`spawn` 失败时保存错误信息；新增 `get-backend-status` IPC |
| `frontend/electron/preload.cjs` | 暴露 `getBackendStatus` API |
| `frontend/src/api/agent.ts` | 新增 `getBackendStatus()` 函数；扩展 ElectronAPI 类型定义 |
| `frontend/src/stores/config.ts` | `saveConfig` 增加 localStorage 兜底双写；`loadConfig` 失败时从 localStorage 恢复 |
| `frontend/src/views/SettingsView.vue` | 保存失败时调用 `getBackendStatus` 获取详细错误信息 |

### 三层兜底策略

1. **后端磁盘**：`backend/config.py` → `save_config()` → 写入 `config/config.yaml`（原子操作）
2. **前端 localStorage**：即使后端不可达，也能保存到本地，下次启动可恢复
3. **诊断透传**：后端挂掉时，Electron 主进程记录错误，前端 `getBackendStatus` 读取显示详细信息

### 错误提示改进

- 保存失败不再只显示「保存配置失败」
- 会附带具体原因，例如：
  - "后端进程未运行，请确认 Python (python) 已安装并能启动"
  - "后端诊断: 后端进程异常退出 (退出码=1)。可能原因: Python 未安装或配置错误"

---

## 启动命令

```bash
# 后端
cd backend
DEEPSEEK_API_KEY="your-deepseek-api-key" \
/usr/local/bin/python3 server.py

# 前端 dev
cd frontend && npx vite --port 57100

# 前端 preview
cd frontend && npx vite preview --port 57100
```
