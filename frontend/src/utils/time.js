/**
 * 时间格式化工具函数
 * 
 * 后端返回 UTC 时间（带 Z 后缀），前端转换为北京时间（UTC+8）显示
 */

/**
 * 将 UTC 时间字符串转换为北京时间字符串
 * @param {string|Date} date - UTC 时间字符串或 Date 对象
 * @returns {string} 格式化的北京时间字符串，如 "2026/03/12 15:02:11"
 */
export const formatBeijingTime = (date) => {
  if (!date) return '-'
  
  const d = new Date(date)
  
  // 检查是否为有效日期
  if (isNaN(d.getTime())) return '-'
  
  // 后端返回 UTC 时间（带 Z 后缀），需要加 8 小时转换为北京时间
  const beijingTime = new Date(d.getTime() + 8 * 60 * 60 * 1000)
  
  const year = beijingTime.getUTCFullYear()
  const month = String(beijingTime.getUTCMonth() + 1).padStart(2, '0')
  const day = String(beijingTime.getUTCDate()).padStart(2, '0')
  const hour = String(beijingTime.getUTCHours()).padStart(2, '0')
  const minute = String(beijingTime.getUTCMinutes()).padStart(2, '0')
  const second = String(beijingTime.getUTCSeconds()).padStart(2, '0')
  
  return `${year}/${month}/${day} ${hour}:${minute}:${second}`
}

/**
 * 格式化日期（只显示日期部分）
 * @param {string|Date} date - UTC 时间字符串或 Date 对象
 * @returns {string} 格式化的日期字符串，如 "2026/03/12"
 */
export const formatBeijingDate = (date) => {
  if (!date) return '-'
  
  const d = new Date(date)
  
  if (isNaN(d.getTime())) return '-'
  
  const beijingTime = new Date(d.getTime() + 8 * 60 * 60 * 1000)
  
  const year = beijingTime.getUTCFullYear()
  const month = String(beijingTime.getUTCMonth() + 1).padStart(2, '0')
  const day = String(beijingTime.getUTCDate()).padStart(2, '0')
  
  return `${year}/${month}/${day}`
}

/**
 * 格式化时间（只显示时间部分）
 * @param {string|Date} date - UTC 时间字符串或 Date 对象
 * @returns {string} 格式化的时间字符串，如 "15:02:11"
 */
export const formatBeijingTimeOnly = (date) => {
  if (!date) return '-'
  
  const d = new Date(date)
  
  if (isNaN(d.getTime())) return '-'
  
  const beijingTime = new Date(d.getTime() + 8 * 60 * 60 * 1000)
  
  const hour = String(beijingTime.getUTCHours()).padStart(2, '0')
  const minute = String(beijingTime.getUTCMinutes()).padStart(2, '0')
  const second = String(beijingTime.getUTCSeconds()).padStart(2, '0')
  
  return `${hour}:${minute}:${second}`
}

/**
 * 获取当前北京时间
 * @returns {Date} 当前北京时间
 */
export const getCurrentBeijingTime = () => {
  const now = new Date()
  return new Date(now.getTime() + 8 * 60 * 60 * 1000)
}

export default {
  formatBeijingTime,
  formatBeijingDate,
  formatBeijingTimeOnly,
  getCurrentBeijingTime
}
