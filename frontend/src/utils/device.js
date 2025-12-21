/** 设备检测工具 */

/**
 * 检测是否为移动设备
 */
export function isMobile() {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  )
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

