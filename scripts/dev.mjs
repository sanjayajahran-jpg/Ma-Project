import { spawn } from 'node:child_process';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');
const backendDir = path.resolve(rootDir, 'backend');

const isWindows = process.platform === 'win32';
const args = process.argv.slice(2);
const backendOnly = args.includes('--backend-only');
const webOnly = args.includes('--web-only');

// Cari executable Python yang valid (utamakan venv backend)
function getPythonCommand() {
  const venvWindows = path.join(backendDir, 'venv', 'Scripts', 'python.exe');
  const venvUnix = path.join(backendDir, 'venv', 'bin', 'python');

  if (fs.existsSync(venvWindows)) return venvWindows;
  if (fs.existsSync(venvUnix)) return venvUnix;
  return isWindows ? 'python' : 'python3';
}

console.log('='.repeat(65));
console.log('  🚀 EVnesia & CMS Media - Unified Development Server');
console.log('='.repeat(65));

const children = [];

function cleanup() {
  console.log('\n[!] Menghentikan server development...');
  for (const child of children) {
    if (child && !child.killed) {
      if (isWindows) {
        try {
          spawn('taskkill', ['/pid', String(child.pid), '/f', '/t'], { stdio: 'ignore' });
        } catch {
          child.kill('SIGINT');
        }
      } else {
        child.kill('SIGINT');
      }
    }
  }
  process.exit(0);
}

process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);

// 1. Jalankan Backend (FastAPI Python)
if (!webOnly) {
  const pythonCmd = getPythonCommand();
  const runPyPath = path.join(backendDir, 'run.py');

  console.log(`[*] Menjalankan Python Backend menggunakan: ${pythonCmd}`);
  console.log(`    -> URL API Backend : http://localhost:8000`);
  console.log(`    -> Swagger UI Docs : http://localhost:8000/docs`);
  console.log(`    -> Admin Dashboard : http://localhost:8000/admin`);

  const backendProc = spawn(pythonCmd, [runPyPath], {
    cwd: backendDir,
    stdio: 'inherit',
    env: { ...process.env, PYTHONUNBUFFERED: '1' }
  });

  children.push(backendProc);

  backendProc.on('error', (err) => {
    console.error('[BACKEND ERROR] Gagal menjalankan backend:', err.message);
  });

  backendProc.on('exit', (code) => {
    if (code !== 0 && code !== null) {
      console.warn(`[BACKEND EXIT] Backend berhenti dengan kode ${code}`);
    }
  });
}

// 2. Jalankan Frontend (Astro Web)
if (!backendOnly) {
  console.log(`\n[*] Menjalankan Astro Frontend Web...`);
  console.log(`    -> URL Website     : http://localhost:4321`);

  const npmCmd = isWindows ? 'npm.cmd' : 'npm';
  const frontendProc = spawn(npmCmd, ['run', 'dev:web'], {
    cwd: rootDir,
    stdio: 'inherit',
    shell: isWindows,
    env: { ...process.env, ASTRO_DEV_BACKGROUND: '1' }
  });

  children.push(frontendProc);

  frontendProc.on('error', (err) => {
    console.error('[FRONTEND ERROR] Gagal menjalankan frontend:', err.message);
  });

  frontendProc.on('exit', (code) => {
    if (code !== 0 && code !== null) {
      console.warn(`[FRONTEND EXIT] Frontend berhenti dengan kode ${code}`);
    }
  });
}
