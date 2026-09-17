import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import http from 'node:http'
import { spawn } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

/**
 * Vite plugin that checks if FastAPI backend on port 8000 is running.
 * If not already running (and not launched by the root runner), it auto-spawns
 * python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload from backend/
 * so the frontend never gets disconnected.
 */
function autoStartBackendPlugin() {
  let backendProc = null

  const isPortAvailable = () => {
    return new Promise((resolve) => {
      const req = http.get('http://127.0.0.1:8000/api/health', { timeout: 800 }, (res) => {
        resolve(res.statusCode === 200)
      })
      req.on('error', () => resolve(false))
      req.on('timeout', () => {
        req.destroy()
        resolve(false)
      })
    })
  }

  return {
    name: 'auto-start-backend',
    async configureServer(server) {
      // If already launched by root dev script, don't duplicate
      if (process.env.HIV_DEV_RUNNER === '1') {
        return
      }

      const isRunning = await isPortAvailable()
      if (!isRunning) {
        console.log('\n[vite] FastAPI backend is offline. Auto-starting backend on http://127.0.0.1:8000...')
        const backendDir = path.resolve(__dirname, '../backend')
        const isWindows = process.platform === 'win32'
        const command = isWindows ? 'cmd.exe' : 'python'
        const args = isWindows
          ? ['/c', 'python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload']
          : ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000', '--reload']

        backendProc = spawn(command, args, {
          cwd: backendDir,
          stdio: 'inherit',
        })

        backendProc.on('error', (err) => {
          console.error('[vite] Failed to auto-start backend:', err.message)
        })

        const cleanup = () => {
          if (backendProc && !backendProc.killed) {
            try {
              if (isWindows) {
                spawn('taskkill', ['/pid', backendProc.pid.toString(), '/f', '/t'])
              } else {
                backendProc.kill('SIGTERM')
              }
            } catch {
              // Ignore cleanup errors
            }
          }
        }

        process.on('exit', cleanup)
        process.on('SIGINT', cleanup)
        process.on('SIGTERM', cleanup)
      } else {
        console.log('[vite] FastAPI backend verified running on port 8000.')
      }
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), autoStartBackendPlugin()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})

