# 个人资料功能实现文档

## 功能概述

实现了完整的用户个人资料管理功能，用户可以查看和编辑个人信息，包括昵称、性别、年龄，以及修改密码。

## 功能特性

### 1. 个人资料管理
- ✅ 查看用户名和邮箱（只读）
- ✅ 设置/修改昵称（最多50个字符）
- ✅ 选择性别（男/女/其他）
- ✅ 设置年龄（1-150岁）
- ✅ 查看注册时间和账号状态

### 2. 密码管理
- ✅ 修改密码功能
- ✅ 旧密码验证
- ✅ 新密码确认
- ✅ 修改成功后自动退出登录

### 3. 用户体验
- ✅ 表单验证
- ✅ 实时反馈
- ✅ 响应式设计
- ✅ 优雅的错误处理

## 技术实现

### 后端实现

#### 1. 数据库模型更新

**文件**: `backend/app/models/user.py`

添加了三个新字段：
```python
nickname = Column(String(50), nullable=True)  # 昵称
gender = Column(String(10), nullable=True)    # 性别: male, female, other
age = Column(Integer, nullable=True)          # 年龄
```

#### 2. API 接口

**文件**: `backend/app/api/profile.py`

创建了三个 API 端点：

##### GET /api/profile
获取当前用户资料

**响应示例**:
```json
{
  "id": 1,
  "username": "user123",
  "email": "user@example.com",
  "nickname": "小明",
  "gender": "male",
  "age": 12,
  "created_at": "2025-01-01T00:00:00"
}
```

##### PUT /api/profile
更新用户资料

**请求体**:
```json
{
  "nickname": "小明",
  "gender": "male",
  "age": 12
}
```

**验证规则**:
- nickname: 最多50个字符
- gender: 必须是 "male", "female", 或 "other"
- age: 1-150之间的整数

##### POST /api/profile/change-password
修改密码

**请求体**:
```json
{
  "old_password": "旧密码",
  "new_password": "新密码"
}
```

**验证规则**:
- 旧密码必须正确
- 新密码至少6位

#### 3. 路由注册

**文件**: `backend/app/main.py`

```python
from app.api import profile
app.include_router(profile.router)
```

### 前端实现

#### 1. 个人资料页面

**文件**: `frontend/src/views/Profile.vue`

页面包含三个卡片：

##### 基本信息卡片
- 用户名（只读）
- 邮箱（只读）
- 昵称（可编辑）
- 性别（单选）
- 年龄（数字输入）

##### 修改密码卡片
- 旧密码输入
- 新密码输入
- 确认密码输入

##### 账号信息卡片
- 注册时间
- 账号状态

#### 2. 路由配置

**文件**: `frontend/src/router/index.js`

```javascript
{
  path: '/profile',
  name: 'Profile',
  component: () => import('@/views/Profile.vue'),
  meta: { requiresAuth: true, title: '个人资料' }
}
```

#### 3. 导航栏入口

**文件**: `frontend/src/components/NavBar.vue`

在用户下拉菜单中添加"个人资料"选项：
```vue
<el-dropdown-item command="profile">
  <el-icon><User /></el-icon>
  <span>个人资料</span>
</el-dropdown-item>
```

## 数据库迁移

### 迁移脚本

**文件**: `backend/migrate_add_profile_fields.py`

运行迁移：
```bash
cd backend
python migrate_add_profile_fields.py
```

脚本会自动检查字段是否存在，避免重复添加。

### 手动迁移（SQLite）

如果需要手动迁移，执行以下 SQL：
```sql
ALTER TABLE users ADD COLUMN nickname VARCHAR(50);
ALTER TABLE users ADD COLUMN gender VARCHAR(10);
ALTER TABLE users ADD COLUMN age INTEGER;
```

## 使用指南

### 用户操作流程

1. **访问个人资料页面**
   - 点击右上角用户头像
   - 选择"个人资料"

2. **编辑基本信息**
   - 输入昵称
   - 选择性别
   - 输入年龄
   - 点击"保存修改"

3. **修改密码**
   - 输入旧密码
   - 输入新密码
   - 确认新密码
   - 点击"修改密码"
   - 系统会自动退出，需要重新登录

### API 调用示例

#### 获取用户资料
```javascript
const response = await api.get('/profile')
console.log(response)
```

#### 更新用户资料
```javascript
await api.put('/profile', {
  nickname: '小明',
  gender: 'male',
  age: 12
})
```

#### 修改密码
```javascript
await api.post('/profile/change-password', {
  old_password: 'oldpass123',
  new_password: 'newpass456'
})
```

## 表单验证

### 前端验证

#### 基本信息表单
- **昵称**: 最多50个字符
- **年龄**: 1-150之间的整数

#### 密码表单
- **旧密码**: 必填，至少6位
- **新密码**: 必填，至少6位
- **确认密码**: 必填，必须与新密码一致

### 后端验证

使用 Pydantic 模型进行验证：
```python
class ProfileUpdateRequest(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    age: Optional[int] = Field(None, ge=1, le=150)
```

## 安全性

### 密码修改安全
1. **旧密码验证**: 必须提供正确的旧密码
2. **密码加密**: 使用 bcrypt 加密存储
3. **强制重新登录**: 修改密码后自动退出登录

### 权限控制
- 所有 API 都需要认证（JWT Token）
- 用户只能修改自己的资料
- 使用 `get_current_user` 依赖注入确保安全

## 错误处理

### 常见错误

#### 400 Bad Request
- 旧密码不正确
- 数据验证失败

#### 401 Unauthorized
- 未登录或 Token 过期

#### 404 Not Found
- 用户不存在

### 错误提示

前端会显示友好的错误提示：
- "旧密码不正确"
- "更新个人资料失败"
- "修改密码失败"

## 测试

### 手动测试步骤

1. **测试获取资料**
   - 登录系统
   - 访问个人资料页面
   - 验证信息显示正确

2. **测试更新资料**
   - 修改昵称、性别、年龄
   - 点击保存
   - 验证更新成功提示
   - 刷新页面验证数据持久化

3. **测试修改密码**
   - 输入错误的旧密码，验证错误提示
   - 输入正确的旧密码和新密码
   - 验证修改成功并自动退出
   - 使用新密码登录

4. **测试表单验证**
   - 输入超长昵称（>50字符）
   - 输入无效年龄（<1 或 >150）
   - 密码确认不一致
   - 验证错误提示

### API 测试

使用 curl 测试：

```bash
# 获取资料
curl -X GET http://localhost:8000/api/profile \
  -H "Authorization: Bearer YOUR_TOKEN"

# 更新资料
curl -X PUT http://localhost:8000/api/profile \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nickname":"小明","gender":"male","age":12}'

# 修改密码
curl -X POST http://localhost:8000/api/profile/change-password \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"old_password":"oldpass","new_password":"newpass"}'
```

## 样式设计

### 设计特点
- 📱 响应式设计，适配移动端
- 🎨 使用 CSS 变量，支持主题切换
- 💫 流畅的动画效果
- 📦 卡片式布局，清晰分组

### 颜色方案
- 主色调：使用项目统一的 CSS 变量
- 表单：浅色背景，深色文字
- 按钮：主题色高亮

## 文件清单

### 后端文件
- ✅ `backend/app/models/user.py` - 用户模型（已更新）
- ✅ `backend/app/api/profile.py` - 个人资料 API（新增）
- ✅ `backend/app/main.py` - 路由注册（已更新）
- ✅ `backend/migrate_add_profile_fields.py` - 数据库迁移脚本（新增）

### 前端文件
- ✅ `frontend/src/views/Profile.vue` - 个人资料页面（新增）
- ✅ `frontend/src/router/index.js` - 路由配置（已更新）
- ✅ `frontend/src/components/NavBar.vue` - 导航栏（已更新）

### 文档文件
- ✅ `docs/ai/PROFILE_FEATURE.md` - 本文档（新增）

## 后续优化建议

### 功能增强
1. **头像上传**: 允许用户上传自定义头像
2. **邮箱修改**: 支持修改邮箱（需要验证）
3. **账号注销**: 提供账号注销功能
4. **隐私设置**: 控制信息可见性

### 用户体验
1. **实时预览**: 修改时实时预览效果
2. **撤销功能**: 支持撤销修改
3. **修改历史**: 记录资料修改历史
4. **批量操作**: 一次性修改多个字段

### 安全增强
1. **二次验证**: 重要操作需要二次验证
2. **操作日志**: 记录所有修改操作
3. **密码强度**: 检查密码强度
4. **登录设备**: 显示登录设备列表

## 常见问题

### Q: 修改密码后为什么要重新登录？
A: 为了安全考虑，修改密码后会使当前 Token 失效，需要使用新密码重新登录。

### Q: 昵称可以为空吗？
A: 可以，昵称是可选字段。

### Q: 性别可以不选吗？
A: 可以，性别也是可选字段。

### Q: 数据库迁移会影响现有数据吗？
A: 不会，迁移只是添加新字段，不会修改或删除现有数据。

### Q: 如何重置密码？
A: 目前需要知道旧密码才能修改。如果忘记密码，需要联系管理员重置。

## 总结

个人资料功能已经完整实现，包括：
- ✅ 后端 API 和数据模型
- ✅ 前端页面和表单验证
- ✅ 导航栏入口
- ✅ 密码修改功能
- ✅ 数据库迁移脚本
- ✅ 完整的文档

用户现在可以方便地管理自己的个人信息和账号安全。

---

**实现日期**: 2025-12-31  
**版本**: 1.0  
**状态**: ✅ 已完成

