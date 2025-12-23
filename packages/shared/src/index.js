/**
 * 格式化日期
 * @param {Date} date 
 * @returns {string}
 */
export function formatDate(date) {
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

/**
 * 延迟函数
 * @param {number} ms 
 * @returns {Promise<void>}
 */
export function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 生成随机ID
 * @returns {string}
 */
export function generateId() {
  return Math.random().toString(36).substring(2, 9);
}
