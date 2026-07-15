// CPQ Agent App — Electron Preload
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // 平台信息 (darwin | win32 | linux)
  getPlatform: () => ipcRenderer.invoke('get-platform'),
  
  // 窗口大小
  getWindowSize: () => ipcRenderer.invoke('get-window-size'),
  
  // 后端 API 地址
  getBackendUrl: () => ipcRenderer.invoke('get-backend-url'),
  
  // 后端诊断状态
  getBackendStatus: () => ipcRenderer.invoke('get-backend-status'),
  
  // 设置存储
  getSetting: (key) => ipcRenderer.invoke('get-setting', key),
  setSetting: (key, value) => ipcRenderer.invoke('set-setting', key, value),
});
