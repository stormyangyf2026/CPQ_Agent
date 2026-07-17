// CPQ Agent App — Electron Main Process (跨平台版)
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');

let mainWindow = null;
let backendProcess = null;
let backendError = null;  // 记录后端启动错误，供前端查询
const BACKEND_PORT = 58118;

// ── 平台检测 ──────────────────────────────────────────────

const isMac = process.platform === 'darwin';
const isWin = process.platform === 'win32';
const isDev = !app.isPackaged;

// ── 后端路径 ──────────────────────────────────────────────

function getBackendDir() {
  if (isDev) return path.join(__dirname, '..', '..', 'backend');
  const exeDir = path.dirname(app.getPath('exe'));
  return path.join(exeDir, 'resources', 'backend');
}

function getConfigPath() {
  if (isDev) return path.join(__dirname, '..', '..', 'config', 'config.yaml');
  // 通过 exe 所在目录推导，避免 process.resourcesPath 在 Windows 上解析错误
  const exeDir = path.dirname(app.getPath('exe'));
  return path.join(exeDir, 'resources', 'config', 'config.yaml');
}

function findPython() {
  const candidates = isWin
    ? ['python', 'python3', 'py', `${process.env.LOCALAPPDATA}\\Programs\\Python\\Python313\\python.exe`]
    : ['/usr/local/bin/python3.13', '/usr/local/bin/python3', '/opt/homebrew/bin/python3', '/usr/bin/python3', 'python3'];
  for (const p of candidates) {
    if (fs.existsSync(p)) return p;
  }
  return isWin ? 'python' : 'python3';
}

// ── 后端启动 ──────────────────────────────────────────────

function startBackend() {
  return new Promise((resolve, reject) => {
    const backendDir = getBackendDir();
    const configPath = getConfigPath();
    const env = {
      ...process.env,
      PORT: String(BACKEND_PORT),
      HOST: '127.0.0.1',
      PYTHONUNBUFFERED: '1',
      CONFIG_PATH: configPath,
    };

    let cmd, args;

    if (isDev) {
      // 开发模式：Python 源码
      cmd = findPython();
      args = [path.join(backendDir, 'server.py')];
      console.log(`[main] 开发模式: ${cmd} server.py`);
    } else if (isMac) {
      // macOS 生产：PyInstaller 二进制
      const bin = path.join(backendDir, 'cpq-backend');
      if (fs.existsSync(bin)) {
        fs.chmodSync(bin, 0o755);
        cmd = bin;
        args = [];
        console.log(`[main] macOS 生产模式: 独立二进制`);
      } else {
        // 回退到 Python 源码
        cmd = findPython();
        args = [path.join(backendDir, 'server.py')];
        console.log(`[main] macOS 回退: ${cmd} server.py`);
      }
    } else {
      // Windows 生产：优先 PyInstaller 二进制，回退 Python 源码
      const exe = path.join(backendDir, 'cpq-backend.exe');
      if (fs.existsSync(exe)) {
        cmd = exe;
        args = [];
        console.log('[main] Windows 生产模式: 独立 exe');
      } else {
        cmd = findPython();
        args = [path.join(backendDir, 'server.py')];
        console.log(`[main] Windows 回退: ${cmd} server.py`);
      }
    }

    console.log(`[main] 后端 port=${BACKEND_PORT}`);
    console.log(`[main] 配置: ${configPath}`);

    // 确认配置文件存在，如果不存在则记录警告
    if (!fs.existsSync(configPath)) {
      console.error(`[main] ⚠️ 配置文件不存在: ${configPath}`);
    }

    backendProcess = spawn(cmd, args, {
      cwd: backendDir,
      env,
      stdio: ['pipe', 'pipe', 'pipe'],
      shell: isWin, // Windows 需要 shell 来解析 PATH
    });

    let started = false;
    let output = '';

    backendProcess.stdout.on('data', (data) => {
      output += data.toString();
      const line = data.toString().trim();
      if (line) console.log(`[backend] ${line}`);
      if (!started && (output.includes('Application startup complete') || output.includes('服务启动完成'))) {
        started = true;
        resolve();
      }
    });

    backendProcess.stderr.on('data', (data) => {
      output += data.toString();
      console.error(`[backend:err] ${data.toString().trim()}`);
    });

    backendProcess.on('error', (err) => {
      const msg = `后端进程启动失败: ${err.message}`;
      console.error(`[main] ${msg}`);
      backendError = msg;
      if (!started) reject(err);
    });

    backendProcess.on('close', (code) => {
      const msg = `后端进程异常退出 (退出码=${code})。可能原因: Python 未安装或配置错误。`;
      console.log(`[main] ${msg}`);
      backendError = msg;
      backendProcess = null;
      if (!started) reject(new Error(`Backend exited with code ${code}`));
    });

    setTimeout(() => {
      if (!started) {
        console.log('[main] 后端启动超时，尝试继续...');
        resolve();
      }
    }, 20000);
  });
}

function stopBackend() {
  if (backendProcess) {
    console.log('[main] 关闭后端...');
    backendProcess.kill('SIGTERM');
    backendProcess = null;
  }
}

function checkBackendHealth() {
  return new Promise((resolve) => {
    const req = http.get(`http://127.0.0.1:${BACKEND_PORT}/health`, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data).status === 'ok' || JSON.parse(data).status === 'degraded'); }
        catch { resolve(false); }
      });
    });
    req.on('error', () => resolve(false));
    req.setTimeout(3000, () => { req.destroy(); resolve(false); });
  });
}

async function waitForBackend(maxRetries = 30) {
  for (let i = 0; i < maxRetries; i++) {
    if (await checkBackendHealth()) { console.log('[main] 后端就绪'); return true; }
    await new Promise(r => setTimeout(r, 1000));
  }
  console.error('[main] 后端就绪超时');
  return false;
}

// ── 窗口管理 ──────────────────────────────────────────────

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    title: 'CPQ Agent - 智能配单',
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    titleBarStyle: isMac ? 'hiddenInset' : 'default',
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:57100');
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'));
  }

  mainWindow.on('closed', () => { mainWindow = null; });
}

// ── IPC ──────────────────────────────────────────────────

ipcMain.handle('get-platform', () => process.platform);
ipcMain.handle('get-backend-url', () =>
  isDev ? 'http://localhost:58100' : `http://127.0.0.1:${BACKEND_PORT}`
);
ipcMain.handle('get-window-size', () => {
  if (!mainWindow) return { width: 1280, height: 800 };
  const [width, height] = mainWindow.getSize();
  return { width, height };
});
ipcMain.handle('get-backend-status', () => ({
  running: backendProcess !== null,
  error: backendError,
  port: BACKEND_PORT,
  pythonFound: findPython(),
  backendDir: getBackendDir(),
  configPath: getConfigPath(),
}));

// ── 生命周期 ──────────────────────────────────────────────

app.whenReady().then(async () => {
  if (isDev) {
    console.log('[main] 开发模式，跳过自动启动后端');
    createWindow();
  } else {
    let backendReady = true;
    try {
      await startBackend();
      backendReady = await waitForBackend();
    } catch (err) {
      console.error('[main] 后端启动异常:', err);
      backendReady = false;
    }
    createWindow();
    if (!backendReady) {
      // 窗口加载完成后弹出后端错误提示
      const errorMsg = backendError
        ? `后端启动失败: ${backendError}\n\n请检查:\n1. 防火墙是否拦截了端口 ${BACKEND_PORT}\n2. 是否有其他程序占用了 ${BACKEND_PORT} 端口\n3. 杀毒软件是否误杀了 cpq-backend.exe`
        : `后端无法连接，请检查:\n1. 防火墙是否拦截了端口 ${BACKEND_PORT}\n2. 是否有其他程序占用了 ${BACKEND_PORT} 端口`;
      mainWindow?.webContents.on('did-finish-load', () => {
        mainWindow?.webContents.executeJavaScript(`
          setTimeout(() => {
            alert(${JSON.stringify(errorMsg)});
          }, 500);
        `);
      });
    }
  }
});

app.on('before-quit', stopBackend);
app.on('window-all-closed', () => { if (!isMac) app.quit(); });
app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
