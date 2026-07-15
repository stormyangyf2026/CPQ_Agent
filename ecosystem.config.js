/**
 * PM2 Ecosystem Config — CPQ Agent App
 * 用法: pm2 start ecosystem.config.js
 *      pm2 status
 *      pm2 logs
 *      pm2 restart all
 *      pm2 stop all
 */

const CPQ_ROOT = "/Users/mac/Library/Mobile Documents/com~apple~CloudDocs/创新万维/0004. platform_dev/005_CPQ_Agent"

module.exports = {
  apps: [
    // ========================================
    // 后端 — FastAPI + LangChain Agent
    // ========================================
    {
      name: "cpq-backend",
      cwd: `${CPQ_ROOT}/backend`,
      script: "/usr/local/bin/python3.13",
      args: "server.py",
      interpreter: "none",          // 不经过 node，直接用 python
      env: {
        PYTHONUNBUFFERED: "1",
        DEEPSEEK_API_KEY: "your-deepseek-api-key"
      },
      // 健康检查
      wait_ready: true,
      listen_timeout: 15000,
      kill_timeout: 5000,
      // 端口冲突则重启
      max_restarts: 5,
      restart_delay: 3000,
      // 日志
      error_file: `${CPQ_ROOT}/logs/backend-error.log`,
      out_file: `${CPQ_ROOT}/logs/backend-out.log`,
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      merge_logs: true,
      // 自动重启 — 进程崩了自动拉起来
      autorestart: true,
      watch: false
    },

    // ========================================
    // 前端 — Vite Dev Server (开发模式)
    // ========================================
    {
      name: "cpq-frontend",
      cwd: `${CPQ_ROOT}/frontend`,
      script: "npx",
      args: "vite --port 57100 --host 0.0.0.0",
      // 健康检查
      wait_ready: false,
      listen_timeout: 10000,
      kill_timeout: 5000,
      max_restarts: 5,
      restart_delay: 3000,
      error_file: `${CPQ_ROOT}/logs/frontend-error.log`,
      out_file: `${CPQ_ROOT}/logs/frontend-out.log`,
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      merge_logs: true,
      autorestart: true,
      watch: false
    },

    // ========================================
    // 前端 — Vite Preview (生产预览)
    // ========================================
    {
      name: "cpq-frontend-preview",
      cwd: `${CPQ_ROOT}/frontend`,
      script: "npx",
      args: "vite preview --port 57100 --host 0.0.0.0",
      env: {
        NODE_ENV: "production"
      },
      wait_ready: false,
      listen_timeout: 10000,
      kill_timeout: 5000,
      max_restarts: 3,
      restart_delay: 3000,
      error_file: `${CPQ_ROOT}/logs/frontend-preview-error.log`,
      out_file: `${CPQ_ROOT}/logs/frontend-preview-out.log`,
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      merge_logs: true,
      autorestart: true,
      watch: false
    }
  ]
}
