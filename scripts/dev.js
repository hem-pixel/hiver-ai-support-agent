#!/usr/bin/env node

/**
 * Cross-platform development runner for Hiver AI Support Agent.
 * Starts the FastAPI backend from backend/ (ensuring app.main:app resolves)
 * and the Vite/React frontend from frontend/.
 *
 * Usage:
 *   node scripts/dev.js            # Starts both backend and frontend
 *   node scripts/dev.js --backend  # Starts backend only
 *   node scripts/dev.js --frontend # Starts frontend only
 */

const { spawn, exec } = require('child_process');
const path = require('path');
const process = require('process');

const ROOT_DIR = path.resolve(__dirname, '..');
const BACKEND_DIR = path.join(ROOT_DIR, 'backend');
const FRONTEND_DIR = path.join(ROOT_DIR, 'frontend');

const args = process.argv.slice(2);
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
Hiver AI Support Agent - Development Runner

Usage:
  node scripts/dev.js            Start both backend and frontend concurrently
  node scripts/dev.js --backend  Start only the FastAPI backend (port 8000)
  node scripts/dev.js --frontend Start only the Vite React frontend (port 5173)

Requirements:
  - Python with requirements installed in backend/
  - Node.js & dependencies installed in frontend/
`);
  process.exit(0);
}

const onlyBackend = args.includes('--backend');
const onlyFrontend = args.includes('--frontend');
const runBackend = onlyBackend || (!onlyBackend && !onlyFrontend);
const runFrontend = onlyFrontend || (!onlyBackend && !onlyFrontend);

const children = [];

function killChild(child) {
  if (!child || child.killed) return;
  if (process.platform === 'win32') {
    try {
      exec(`taskkill /pid ${child.pid} /T /F`, () => {});
    } catch {
      try {
        child.kill('SIGKILL');
      } catch {}
    }
  } else {
    try {
      child.kill('SIGTERM');
    } catch {}
  }
}

function cleanExit(code = 0) {
  for (const child of children) {
    killChild(child);
  }
  process.exit(code);
}

process.on('SIGINT', () => {
  console.log('\n[dev] Shutting down services...');
  cleanExit(0);
});

process.on('SIGTERM', () => {
  cleanExit(0);
});

process.on('exit', () => {
  for (const child of children) {
    killChild(child);
  }
});

function prefixStream(stream, prefix, color) {
  if (!stream) return;
  let buffer = '';
  stream.on('data', (chunk) => {
    buffer += chunk.toString();
    const lines = buffer.split(/\r?\n/);
    buffer = lines.pop(); // keep partial line in buffer
    for (const line of lines) {
      if (line.trim().length > 0) {
        console.log(`${color}${prefix}\x1b[0m ${line}`);
      }
    }
  });
  stream.on('end', () => {
    if (buffer.trim().length > 0) {
      console.log(`${color}${prefix}\x1b[0m ${buffer}`);
    }
  });
}

console.log('====================================================');
console.log(' Starting Hiver AI Support Agent Development Environment');
console.log('====================================================');

if (runBackend) {
  console.log(`[setup] Starting backend from: ${BACKEND_DIR}`);
  console.log('[setup] Command: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload');
  console.log('[setup] Backend Health URL: http://127.0.0.1:8000/api/health');

  const pythonBin = process.env.PYTHON || 'python';
  const backendProcess = spawn(
    pythonBin,
    ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000', '--reload'],
    {
      cwd: BACKEND_DIR,
      env: { ...process.env, PYTHONUNBUFFERED: '1' },
      stdio: ['inherit', 'pipe', 'pipe'],
    }
  );

  prefixStream(backendProcess.stdout, '[backend]', '\x1b[36m'); // Cyan
  prefixStream(backendProcess.stderr, '[backend]', '\x1b[33m'); // Yellow

  backendProcess.on('error', (err) => {
    console.error(`\x1b[31m[backend error]\x1b[0m Failed to start backend: ${err.message}`);
    console.error(`Ensure python is installed and available in PATH, or set the PYTHON environment variable.`);
  });

  backendProcess.on('exit', (code, signal) => {
    if (code !== 0 && code !== null) {
      console.error(`\x1b[31m[backend]\x1b[0m Process exited with code ${code}`);
    }
    if (runFrontend && !onlyBackend) {
      // If backend died unexpectedly while running both, notify user
      console.log(`[dev] Backend stopped.`);
    }
  });

  children.push(backendProcess);
}

if (runFrontend) {
  console.log(`[setup] Starting frontend from: ${FRONTEND_DIR}`);
  console.log('[setup] Command: npm run dev');
  console.log('[setup] Frontend URL: http://localhost:5173');

  const npmCmd = process.platform === 'win32' ? 'npm.cmd' : 'npm';
  const frontendProcess = spawn(
    npmCmd,
    ['run', 'dev'],
    {
      cwd: FRONTEND_DIR,
      env: process.env,
      stdio: ['inherit', 'pipe', 'pipe'],
    }
  );

  prefixStream(frontendProcess.stdout, '[frontend]', '\x1b[32m'); // Green
  prefixStream(frontendProcess.stderr, '[frontend]', '\x1b[35m'); // Magenta

  frontendProcess.on('error', (err) => {
    console.error(`\x1b[31m[frontend error]\x1b[0m Failed to start frontend: ${err.message}`);
    console.error(`Ensure npm is installed and dependencies in frontend/ are installed with 'npm install'.`);
  });

  frontendProcess.on('exit', (code, signal) => {
    if (code !== 0 && code !== null) {
      console.error(`\x1b[31m[frontend]\x1b[0m Process exited with code ${code}`);
    }
  });

  children.push(frontendProcess);
}

console.log('====================================================\n');
