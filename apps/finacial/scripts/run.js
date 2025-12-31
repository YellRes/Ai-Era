/**
 * 跨平台运行 Python 虚拟环境中的命令
 * 用法: node scripts/run.js <command> [args...]
 */
const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

// 获取命令行参数（跳过 node 和脚本路径）
const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('请指定要运行的命令');
  process.exit(1);
}

const command = args[0];
const commandArgs = args.slice(1);

// 根据操作系统确定虚拟环境路径
const isWindows = os.platform() === 'win32';
const venvBin = isWindows ? '.venv\\Scripts' : '.venv/bin';
const ext = isWindows ? '.exe' : '';

// 构建完整的命令路径
const fullCommand = path.join(venvBin, command + ext);

console.log(`运行: ${fullCommand} ${commandArgs.join(' ')}`);

// 执行命令
const proc = spawn(fullCommand, commandArgs, {
  stdio: 'inherit',
  shell: true,
  cwd: process.cwd()
});

proc.on('error', (err) => {
  console.error(`执行失败: ${err.message}`);
  process.exit(1);
});

proc.on('close', (code) => {
  process.exit(code);
});
