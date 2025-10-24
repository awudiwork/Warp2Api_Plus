# Warp 注册功能逐步测试指南

本目录包含 5 个独立的测试脚本，用于逐步验证和修复 Warp 账号注册流程。

## 📋 测试流程概览

```
步骤1: Firebase sendOobCode
    ↓
步骤2: 邮件接收与验证链接提取
    ↓
步骤3: signInWithEmailLink
    ↓
步骤4: Warp GraphQL 激活
    ↓
步骤5: 获取 Warp JWT
```

## 🚀 使用方法

### 准备工作

1. 准备一个测试邮箱（推荐使用 Outlook）
2. 确保代理配置正确（如果需要）
3. 安装依赖：`pip install httpx`

### 测试步骤

#### **步骤 1: 测试发送验证邮件**

```bash
cd test_register
python step1_test_firebase_sendoobcode.py
```

**修改配置**:
- `TEST_EMAIL`: 你的测试邮箱
- `PROXY_URL`: 代理地址（如果需要）

**期望结果**:
- ✅ HTTP 200
- ✅ 收到包含验证链接的邮件

**如果失败**:
- 检查 Firebase API Key 是否正确
- 尝试不同的 payload 配置
- 检查网络连接和代理

---

#### **步骤 2: 测试邮件提取**

```bash
python step2_test_email_extraction.py
```

**功能**:
1. 测试验证链接提取的正则表达式
2. 测试 Microsoft Graph API 获取邮件

**修改配置**:
- `TEST_EMAIL`: 你的测试邮箱
- `OUTLOOK_ACCESS_TOKEN`: Outlook API access token（可选）

**期望结果**:
- ✅ 能从邮件 HTML 中提取 oobCode
- ✅ 正则表达式能匹配不同格式的验证链接

**如果失败**:
- 检查邮件格式是否改变
- 尝试不同的正则表达式
- 手动从邮件中复制验证链接分析

---

#### **步骤 3: 测试邮箱登录**

```bash
python step3_test_signin.py
```

**修改配置**:
- `TEST_EMAIL`: 你的测试邮箱
- `OOB_CODE`: 从步骤2提取的验证码

**期望结果**:
- ✅ HTTP 200
- ✅ 获得 `idToken` 和 `refreshToken`
- ✅ tokens 自动保存到 `tokens.json`

**如果失败**:
- 检查 oobCode 是否过期（通常10分钟有效）
- 检查 oobCode 是否完整
- 重新运行步骤1获取新的验证邮件

---

#### **步骤 4: 测试 Warp 账号激活**

```bash
python step4_test_warp_activate.py
```

**自动配置**: 从 `tokens.json` 读取 idToken

**期望结果**:
- ✅ HTTP 200
- ✅ 返回 `uid` (Warp 用户ID)
- ✅ 账号激活成功

**如果失败**:
- 检查 idToken 是否过期
- 检查 Warp GraphQL API 是否有变化
- 查看错误消息判断问题

---

#### **步骤 5: 测试获取 JWT**

```bash
python step5_test_get_jwt.py
```

**自动配置**: 从 `tokens.json` 读取 refreshToken

**期望结果**:
- ✅ HTTP 200
- ✅ 获得 Warp JWT Token
- ✅ JWT 保存到 `warp_jwt.json`

**如果失败**:
- 检查 refreshToken 是否有效
- 检查 Firebase API Key
- 检查 Warp token 端点是否有变化

---

## 📁 输出文件

测试过程中会生成以下文件：

```
test_register/
├── tokens.json          # Firebase tokens (step3)
├── warp_user.json       # Warp 用户信息 (step4)
└── warp_jwt.json        # Warp JWT Token (step5)
```

---

## 🔧 调试技巧

### 1. 启用详细日志

每个脚本都会输出详细的请求和响应信息，仔细阅读可以发现问题。

### 2. 使用 Burp Suite 抓包

如果需要分析官方客户端的请求：
1. 安装 Burp Suite
2. 配置代理到 Burp
3. 手动注册一个账号
4. 对比请求参数

### 3. 检查 API 变化

官方可能更新了以下内容：
- 新增必填字段
- 修改参数名称
- 更改 API 端点
- 新增验证逻辑

### 4. 查看错误代码

Firebase 常见错误：
- `EXPIRED_OOB_CODE`: ���证码过期
- `INVALID_OOB_CODE`: 验证码无效
- `EMAIL_NOT_FOUND`: 邮箱未找到
- `TOO_MANY_ATTEMPTS_TRY_LATER`: 请求过于频繁

---

## 📝 修复流程

如果某个步骤失败：

1. **记录错误信息**
   - HTTP 状态码
   - 错误消息
   - 请求参数

2. **分析原因**
   - API 端点是否正确
   - 参数是否完整
   - 认证是否有效

3. **修改代码**
   - 更新 `warp_register.py` 中对应的函数
   - 调整 payload 格式
   - 更新正则表达式

4. **重新测试**
   - 运行修改后的测试脚本
   - 验证修复是否有效

5. **更新主程序**
   - 将修复应用到 `warp_register.py`
   - 测试完整注册流程

---

## 💡 常见问题

### Q1: 无法收到验证邮件

**可能原因**:
- Firebase API Key 错误
- 邮件被归类为垃圾邮件
- Outlook 账号问题

**解决方法**:
- 检查垃圾邮件文件夹
- 更换邮箱测试
- 确认 API Key 有效

### Q2: oobCode 一直显示过期

**可能原因**:
- 本地时间不准确
- 网络延迟过大
- 邮件接收延迟

**解决方法**:
- 同步系统时间
- 减少等待时间
- 手动快速提取 oobCode

### Q3: GraphQL 请求失败

**可能原因**:
- Warp 更新了 GraphQL schema
- 需要新的必填字段
- 认证方式改变

**解决方法**:
- 使用 Burp 抓包对比
- 查看 Warp 更新日志
- 测试不同的 query 格式

---

## 🎯 成功标准

所有 5 个步骤都应该返回 ✅ 成功标志。如果某个步骤失败，需要先修复该步骤才能继续。

完成所有测试后，你应该获得：
- ✅ 有效的 Firebase idToken
- ✅ 有效的 Firebase refreshToken
- ✅ 激活的 Warp 账号（uid）
- ✅ 有效的 Warp JWT Token

---

## 📧 支持

如果遇到无法解决的问题：
1. 保存所有测试输出
2. 记录详细的错误信息
3. 提供测试环境信息（Python 版本、操作系统等）
