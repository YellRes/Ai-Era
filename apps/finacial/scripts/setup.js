/**
 * 跨平台安装脚本
 * 自动创建虚拟环境、安装依赖和 Playwright
 */
const { execSync, spawn } = require('child_process');
const os = require('os');
const fs = require('fs');
const path = require('path');

const isWindows = os.platform() === 'win32';
const venvPath = '.venv';
const pipPath = isWindows ? '.venv\\Scripts\\pip' : '.venv/bin/pip';
const playwrightPath = isWindows ? '.venv\\Scripts\\playwright' : '.venv/bin/playwright';

// 镜像源
const mirrorUrl = 'https://pypi.tuna.tsinghua.edu.cn/simple/';

function run(command, description) {
    console.log(`\n📦 ${description}...`);
    console.log(`   执行: ${command}\n`);
    try {
        execSync(command, { stdio: 'inherit', shell: true });
        return true;
    } catch (error) {
        console.error(`❌ ${description} 失败`);
        return false;
    }
}

async function main() {
    console.log('====================================');
    console.log('🚀 财务报表分析系统 - 环境安装');
    console.log(`📍 操作系统: ${isWindows ? 'Windows' : 'macOS/Linux'}`);
    console.log('====================================');

    // 1. 创建虚拟环境
    if (!fs.existsSync(venvPath)) {
        if (!run('python -m venv .venv', '创建虚拟环境')) {
            // 如果 python 不存在，尝试 python3
            if (!run('python3 -m venv .venv', '创建虚拟环境 (python3)')) {
                process.exit(1);
            }
        }
    } else {
        console.log('\n✅ 虚拟环境已存在');
    }

    // 2. 升级 pip
    run(`${pipPath} install --upgrade pip -i ${mirrorUrl}`, '升级 pip');

    // 3. 安装依赖
    if (!run(`${pipPath} install -r requirements.txt -i ${mirrorUrl}`, '安装 Python 依赖')) {
        process.exit(1);
    }

    // 4. 安装 Playwright 浏览器
    console.log('\n📦 安装 Playwright Chromium 浏览器...');
    console.log('   (这可能需要几分钟，请耐心等待)\n');
    if (!run(`${playwrightPath} install chromium`, '安装 Playwright 浏览器')) {
        console.log('\n⚠️  Playwright 浏览器安装失败，但不影响其他功能');
    }

    console.log('\n====================================');
    console.log('✅ 安装完成！');
    console.log('====================================');
    console.log('\n启动服务:');
    console.log('  pnpm run dev:service');
    console.log('  或');
    console.log('  npm run dev');
    console.log('\n访问地址:');
    console.log('  API: http://localhost:8000');
    console.log('  文档: http://localhost:8000/docs');
    console.log('');
}

main();
