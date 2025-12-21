/** 移动端音频工具 */

/**
 * 检查浏览器是否支持Web Speech API
 */
export function isSpeechRecognitionSupported() {
  return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
}

/**
 * 获取SpeechRecognition实例
 */
export function getSpeechRecognition() {
  if ('webkitSpeechRecognition' in window) {
    return new webkitSpeechRecognition()
  } else if ('SpeechRecognition' in window) {
    return new SpeechRecognition()
  }
  return null
}

/**
 * 请求麦克风权限
 */
export async function requestMicrophonePermission() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    stream.getTracks().forEach(track => track.stop())
    return true
  } catch (error) {
    console.error('麦克风权限请求失败:', error)
    return false
  }
}

/**
 * 检查是否为iOS设备
 */
export function isIOSDevice() {
  return /iPad|iPhone|iPod/.test(navigator.userAgent)
}

/**
 * 检查是否为Android设备
 */
export function isAndroidDevice() {
  return /Android/.test(navigator.userAgent)
}

