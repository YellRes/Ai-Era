/**
 * 跨平台清理脚本
 */
const fs = require('fs');
const path = require('path');

const dirsToClean = [
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache'
];

function deleteFolderRecursive(folderPath) {
    if (fs.existsSync(folderPath)) {
        fs.readdirSync(folderPath).forEach((file) => {
            const curPath = path.join(folderPath, file);
            if (fs.lstatSync(curPath).isDirectory()) {
                deleteFolderRecursive(curPath);
            } else {
                fs.unlinkSync(curPath);
            }
        });
        fs.rmdirSync(folderPath);
        return true;
    }
    return false;
}

function findAndClean(dir, targetDirs) {
    let cleaned = 0;

    try {
        const items = fs.readdirSync(dir);

        for (const item of items) {
            const fullPath = path.join(dir, item);

            try {
                const stat = fs.statSync(fullPath);

                if (stat.isDirectory()) {
                    if (targetDirs.includes(item)) {
                        if (deleteFolderRecursive(fullPath)) {
                            console.log(`🗑️  已删除: ${fullPath}`);
                            cleaned++;
                        }
                    } else if (!item.startsWith('.') && item !== 'node_modules' && item !== '.venv') {
                        cleaned += findAndClean(fullPath, targetDirs);
                    }
                }
            } catch (err) {
                // 忽略权限错误
            }
        }
    } catch (err) {
        // 忽略目录读取错误
    }

    return cleaned;
}

console.log('🧹 清理 Python 缓存文件...\n');
const cleaned = findAndClean(process.cwd(), dirsToClean);
console.log(`\n✅ 清理完成，共删除 ${cleaned} 个目录`);
