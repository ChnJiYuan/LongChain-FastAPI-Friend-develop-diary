const { app, BrowserWindow } = require('electron')
const path = require('path')
const fs = require('fs')

// Flags
const isDevEnv = process.env.NODE_ENV === 'development'
const forceDevServer = process.env.ELECTRON_FORCE_DEV === '1'
const forceDevtools = process.env.ELECTRON_OPEN_DEVTOOLS === '1'
const devUrl = process.env.ELECTRON_DEV_URL || 'http://localhost:5173'

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 900,
    minWidth: 900,
    minHeight: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
    },
  })

  if (isDevEnv || forceDevServer) {
    win.loadURL(devUrl)
    win.webContents.openDevTools({ mode: 'detach' })
  } else {
    const candidate = path.join(__dirname, '..', 'dist', 'index.html')
    const fallback = path.join(process.resourcesPath, 'dist', 'index.html')
    const target = fs.existsSync(candidate) ? candidate : fallback
    console.log('[electron] loading html:', target)
    win.loadFile(target)

    // Uncomment for production debugging or set ELECTRON_OPEN_DEVTOOLS=1
    if (forceDevtools) {
      win.webContents.openDevTools({ mode: 'detach' })
    }

    win.webContents.on('did-fail-load', (_e, code, desc, url) => {
      console.error('Load failed', { code, desc, url, target })
    })
    win.webContents.on('console-message', (_e, level, message) => {
      console.log(`Console ${level}: ${message}`)
    })
  }

  win.removeMenu()
}

app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
