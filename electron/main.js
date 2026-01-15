
const { app, BrowserWindow } = require('electron');
const path = require('path');

// Fix: Handle EPIPE errors by safely wrapping console methods
const originalLog = console.log;
const originalError = console.error;

function safeConsoleCall(fn, args) {
  try {
    fn.apply(console, args);
  } catch (err) {
    // Ignore EPIPE errors which happen when the output stream closes
    if (err.code !== 'EPIPE') {
      // For other errors, try to write to stderr directly (if possible) or just ignore to prevent crash
      try {
        process.stderr.write(`Console error: ${err.message}\n`);
      } catch (e) { /* ignore */ }
    }
  }
}

console.log = (...args) => safeConsoleCall(originalLog, args);
console.error = (...args) => safeConsoleCall(originalError, args);

// Fix: Dynamic import for ESM modules in Electron Main Process
let serve;
(async () => {
  const serveModule = await import('electron-serve');
  serve = serveModule.default || serveModule;
})();

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    transparent: true,    // Enable transparency
    frame: false,         // Remove window frame
    alwaysOnTop: true,    // Keep on top of other apps
    hasShadow: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  // Initial load
  const isDev = !app.isPackaged;

  if (isDev) {
    const port = process.env.PORT || 3000;
    mainWindow.loadURL(`http://localhost:${port}`);
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  } else {
    // Only use serve in production
    if (serve) {
      const loadURL = serve({ directory: 'out' });
      loadURL(mainWindow);
    } else {
      console.error("Electron-serve not loaded yet");
    }
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });



  // Ignore mouse events to allow clicking through the transparent parts initially
  mainWindow.setIgnoreMouseEvents(true, { forward: true });

  // Handle mouse events from the renderer to toggle click-through
  mainWindow.webContents.on('ipc-message', (event, channel, ...args) => {
    if (channel === 'set-ignore-mouse-events') {
      const ignore = args[0];
      mainWindow.setIgnoreMouseEvents(ignore, { forward: true });
    }
  });

  // START: Window Polling Logic
  let activeWin;
  (async () => {
    try {
      const mod = await import('active-win');
      activeWin = mod.default || mod; // Handle both ESM default and CommonJS
    } catch (e) {
      console.error('Failed to load active-win:', e);
    }
  })();

  setInterval(async () => {
    if (mainWindow && activeWin) {
      try {
        const result = await activeWin(); // Call the function directly
        if (result) {
          // Send the active window info to the renderer
          mainWindow.webContents.send('active-window-change', {
            title: result.title,
            owner: result.owner.name,
            app: result.owner.path
          });
        }
      } catch (error) {
        console.error('[Window Poller Error]:', error); // Likely Permission Denied on macOS
      }
    }
  }, 500); // Poll every 500ms

  // END: Window Polling Logic

}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});
