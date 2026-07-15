import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  base: './',
  plugins: [
    vue(),
    // Electron file:// 协议兼容：移除 crossorigin 属性
    // Vite 构建时会自动添加 crossorigin，但在 Electron file:// 中会导致资源加载失败
    {
      name: 'electron-compat',
      enforce: 'post',
      transformIndexHtml(html) {
        return html.replace(/\s+crossorigin(?:="[^"]*")?/g, '')
      },
    },
  ],
})
