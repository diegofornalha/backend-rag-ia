import { spawn, ChildProcess } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import chalk from 'chalk';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = resolve(__dirname, '..');

interface ProcessConfig {
  name: string;
  command: string;
  args: string[];
  cwd: string;
  color: 'blue' | 'green' | 'yellow' | 'magenta';
  logPrefix?: string;
}

const processes: ProcessConfig[] = [
  {
    name: 'Backend',
    command: 'python',
    args: ['-m', 'uvicorn', 'main:app', '--reload'],
    cwd: rootDir,
    color: 'blue',
    logPrefix: '🔹'
  },
  {
    name: 'Frontend',
    command: 'yarn',
    args: ['dev'],
    cwd: resolve(rootDir, 'frontend'),
    color: 'green',
    logPrefix: '🔸'
  }
];

const runningProcesses: ChildProcess[] = [];

function formatLog(config: ProcessConfig, message: string): string {
  const timestamp = new Date().toLocaleTimeString();
  const prefix = config.logPrefix || '';
  return chalk[config.color](`${prefix} [${timestamp}] [${config.name}] ${message}`);
}

function cleanLog(log: string): string {
  // Remove códigos ANSI e caracteres de controle
  return log.replace(/\u001b\[\d+m/g, '').trim();
}

function isErrorLog(log: string): boolean {
  const lowerLog = log.toLowerCase();
  return lowerLog.includes('error') || lowerLog.includes('erro') || lowerLog.includes('exception');
}

function isInfoLog(log: string): boolean {
  return log.toLowerCase().includes('info');
}

function startProcess(config: ProcessConfig): Promise<void> {
  return new Promise((resolve, reject) => {
    console.log(formatLog(config, 'Iniciando...'));
    
    const process = spawn(config.command, config.args, {
      cwd: config.cwd,
      stdio: 'pipe',
      shell: true
    });

    process.stdout?.on('data', (data) => {
      const lines = data.toString().split('\n');
      lines.forEach(line => {
        const cleanedLine = cleanLog(line);
        if (cleanedLine) {
          if (isErrorLog(cleanedLine)) {
            console.error(chalk.red(formatLog(config, cleanedLine)));
          } else if (isInfoLog(cleanedLine)) {
            console.log(chalk.gray(formatLog(config, cleanedLine)));
          } else {
            console.log(formatLog(config, cleanedLine));
          }
        }
      });
    });

    process.stderr?.on('data', (data) => {
      const lines = data.toString().split('\n');
      lines.forEach(line => {
        const cleanedLine = cleanLog(line);
        if (cleanedLine) {
          console.error(chalk.red(formatLog(config, `ERRO: ${cleanedLine}`)));
        }
      });
    });

    process.on('error', (error) => {
      console.error(chalk.red(formatLog(config, `Erro ao iniciar: ${error.message}`)));
      reject(error);
    });

    process.on('exit', (code) => {
      if (code !== 0) {
        console.error(chalk.red(formatLog(config, `Processo encerrou com código ${code}`)));
        reject(new Error(`${config.name} encerrou com código ${code}`));
      } else {
        console.log(formatLog(config, 'Processo encerrado com sucesso'));
        resolve();
      }
    });

    runningProcesses.push(process);
  });
}

async function main() {
  console.log(chalk.cyan('\n=== Iniciando ambiente de desenvolvimento ===\n'));

  try {
    await Promise.all(processes.map(startProcess));
    console.log(chalk.green('\n✓ Ambiente de desenvolvimento iniciado'));
    console.log(chalk.yellow('Pressione Ctrl+C para encerrar todos os processos\n'));
  } catch (error) {
    if (error instanceof Error) {
      console.error(chalk.red(`\n✗ Erro ao iniciar ambiente: ${error.message}`));
    } else {
      console.error(chalk.red('\n✗ Erro desconhecido ao iniciar ambiente'));
    }
    cleanup();
    process.exit(1);
  }
}

function cleanup() {
  console.log(chalk.yellow('\nEncerrando processos...'));
  runningProcesses.forEach(process => {
    process.kill();
  });
}

process.on('SIGINT', () => {
  console.log(chalk.yellow('\nRecebido sinal de interrupção'));
  cleanup();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log(chalk.yellow('\nRecebido sinal de término'));
  cleanup();
  process.exit(0);
});

process.on('uncaughtException', (error: Error) => {
  console.error(chalk.red(`\nErro não tratado: ${error.message}`));
  cleanup();
  process.exit(1);
});

main(); 