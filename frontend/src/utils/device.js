/** 设备检测工具 */

/**
 * 检测是否为移动设备
 * 注意：当前应用在移动端和桌面端使用相同的 UI 布局
 * 此函数保留用于其他可能需要的场景
 */
export function isMobile() {
  // 检测 User Agent
  const isMobileUA = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  )
  
  // 检测屏幕宽度（移动端通常 <= 768px）
  const isMobileWidth = window.innerWidth <= 768
  
  // 只要满足其中一个条件就认为是移动设备
  return isMobileUA || isMobileWidth
}

/**
 * 检测是否为平板设备
 */
export function isTablet() {
  return /iPad|Android/i.test(navigator.userAgent) && window.innerWidth >= 768
}

/**
 * 检测是否为iOS设备
 */
export function isIOS() {
  return /iPad|iPhone|iPod/.test(navigator.userAgent)
}

/**
 * 检测是否为Android设备
 */
export function isAndroid() {
  return /Android/.test(navigator.userAgent)
}

/**
 * 获取设备类型
 */
export function getDeviceType() {
  if (isTablet()) return 'tablet'
  if (isMobile()) return 'mobile'
  return 'desktop'
}

/**
 * 检测是否支持触摸
 */
export function isTouchDevice() {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0
}

