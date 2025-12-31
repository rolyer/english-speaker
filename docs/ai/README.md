# AI 生成的文档索引

本目录包含了在开发过程中由 AI 助手生成的各类技术文档和实现说明。

## 📑 文档分类

### 🎨 UI/UX 改进
- [UNIFIED_UI.md](./UNIFIED_UI.md) - 统一 UI 设计
- [VOICE_UI_REDESIGN.md](./VOICE_UI_REDESIGN.md) - 语音界面重新设计
- [VOICE_BUBBLE_UI.md](./VOICE_BUBBLE_UI.md) - 语音气泡 UI
- [VOICE_CARD_LAYOUT.md](./VOICE_CARD_LAYOUT.md) - 语音卡片布局
- [VOICE_MESSAGE_MENU.md](./VOICE_MESSAGE_MENU.md) - 语音消息菜单
- [NAVBAR_FIX.md](./NAVBAR_FIX.md) - 导航栏修复
- [MOBILE_DETECTION_FIX.md](./MOBILE_DETECTION_FIX.md) - 移动端检测修复

### 🔊 音频功能
- [AUDIO_PLAYBACK_STATE_FIX.md](./AUDIO_PLAYBACK_STATE_FIX.md) - 音频播放状态修复
- [AUTO_PLAY_DEBUG.md](./AUTO_PLAY_DEBUG.md) - 自动播放调试
- [AUTOPLAY_FINAL.md](./AUTOPLAY_FINAL.md) - 自动播放最终版本
- [AUTOPLAY_FIX_V2.md](./AUTOPLAY_FIX_V2.md) - 自动播放修复 V2
- [AUTOPLAY_FIX_V3.md](./AUTOPLAY_FIX_V3.md) - 自动播放修复 V3
- [AUTOPLAY_STATE_SYNC.md](./AUTOPLAY_STATE_SYNC.md) - 自动播放状态同步
- [VOICE_AUTO_PLAY_FIX.md](./VOICE_AUTO_PLAY_FIX.md) - 语音自动播放修复
- [TTS_CACHE.md](./TTS_CACHE.md) - TTS 缓存
- [TTS_FIX.md](./TTS_FIX.md) - TTS 修复

### 🗣️ 语音识别
- [VOICE_RECOGNITION_SETUP.md](./VOICE_RECOGNITION_SETUP.md) - 语音识别设置
- [WHISPER_SETUP.md](./WHISPER_SETUP.md) - Whisper 模型设置

### 📊 发音评分
- [PRONUNCIATION_SCORING_IMPLEMENTATION.md](./PRONUNCIATION_SCORING_IMPLEMENTATION.md) - 发音评分实现

### 💬 对话功能
- [CONVERSATION_FEATURE.md](./CONVERSATION_FEATURE.md) - 对话功能
- [COACHING_RULES_ENHANCEMENT.md](./COACHING_RULES_ENHANCEMENT.md) - 教练规则增强

### 📄 分页功能
- [PAGINATION_FEATURE.md](./PAGINATION_FEATURE.md) - 分页功能
- [PAGINATION_SUMMARY.md](./PAGINATION_SUMMARY.md) - 分页总结
- [PAGINATION_IMPLEMENTATION_SUMMARY.md](./PAGINATION_IMPLEMENTATION_SUMMARY.md) - 分页实现总结
- [PAGINATION_TROUBLESHOOTING.md](./PAGINATION_TROUBLESHOOTING.md) - 分页故障排查
- [MESSAGE_PAGINATION_FEATURE.md](./MESSAGE_PAGINATION_FEATURE.md) - 消息分页功能
- [MESSAGE_PAGINATION_SUMMARY.md](./MESSAGE_PAGINATION_SUMMARY.md) - 消息分页总结
- [QUICK_START_PAGINATION.md](./QUICK_START_PAGINATION.md) - 分页快速开始
- [QUICK_START_MESSAGE_PAGINATION.md](./QUICK_START_MESSAGE_PAGINATION.md) - 消息分页快速开始
- [QUICK_TEST_MESSAGE_PAGINATION.md](./QUICK_TEST_MESSAGE_PAGINATION.md) - 消息分页快速测试
- [TEST_PAGINATION_DEBUG.md](./TEST_PAGINATION_DEBUG.md) - 分页调试测试
- [MANUAL_TEST_SCROLL.md](./MANUAL_TEST_SCROLL.md) - 手动滚动测试

### 🌐 国际化
- [TRANSLATION_FIX.md](./TRANSLATION_FIX.md) - 翻译修复

### ✍️ Markdown 支持
- [MARKDOWN_SUPPORT.md](./MARKDOWN_SUPPORT.md) - Markdown 支持

### 📋 实现总结
- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - 实现总结

## 📚 文档使用说明

### 如何查找文档
1. **按功能分类**: 使用上面的分类索引快速定位相关文档
2. **按时间顺序**: 文件名中的版本号（V2, V3）表示迭代顺序
3. **按问题类型**: FIX 结尾的文档通常包含问题修复说明

### 文档命名规范
- `*_FIX.md` - 问题修复文档
- `*_FEATURE.md` - 功能实现文档
- `*_SETUP.md` - 配置设置文档
- `*_SUMMARY.md` - 总结文档
- `*_DEBUG.md` - 调试文档
- `QUICK_*.md` - 快速开始/测试文档

## 🔍 常见问题快速查找

### 音频播放问题
→ 查看 [AUDIO_PLAYBACK_STATE_FIX.md](./AUDIO_PLAYBACK_STATE_FIX.md) 或 [AUTOPLAY_FINAL.md](./AUTOPLAY_FINAL.md)

### 分页功能问题
→ 查看 [PAGINATION_TROUBLESHOOTING.md](./PAGINATION_TROUBLESHOOTING.md)

### 语音识别配置
→ 查看 [WHISPER_SETUP.md](./WHISPER_SETUP.md) 或 [VOICE_RECOGNITION_SETUP.md](./VOICE_RECOGNITION_SETUP.md)

### UI 样式问题
→ 查看 [UNIFIED_UI.md](./UNIFIED_UI.md) 或相关的 UI 文档

### 移动端问题
→ 查看 [MOBILE_DETECTION_FIX.md](./MOBILE_DETECTION_FIX.md)

## 📝 维护说明

### 添加新文档
1. 将新生成的文档放入此目录
2. 更新本 README.md 的分类索引
3. 使用统一的命名规范

### 文档归档
- 过时的文档可以移动到 `archive/` 子目录
- 保留最新版本的文档在主目录

### 文档合并
- 如果多个文档描述同一功能的不同版本，考虑合并为一个综合文档
- 保留版本历史信息

## 🔗 相关资源

- [项目主文档](../) - 返回上级文档目录
- [开发计划](../开发计划.md) - 查看项目开发计划
- [部署文档](../deployment.md) - 查看部署说明
- [Docker 文档](../docker.md) - 查看 Docker 配置

## 📊 统计信息

- **总文档数**: 35 个
- **最后更新**: 2025-12-31
- **主要类别**: UI/UX (7), 音频 (9), 分页 (11), 其他 (8)

---

**注意**: 这些文档是在开发过程中自动生成的，可能包含调试信息和临时解决方案。在参考这些文档时，请以最新版本为准。

