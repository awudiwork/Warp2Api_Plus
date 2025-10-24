# 如何获取新的 Firebase API Key

## 问题
当前所有的 Firebase API Key 都已失效：
- `AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs` - 被 Google 封禁 (API_KEY_SERVICE_BLOCKED)
- 其他备用 Key - 无效 (API_KEY_INVALID)

## 解决方案

### 方案 1: 从 Warp 网页版提取 (推荐)

1. 打开浏览器开发者工具 (F12)
2. 访问 https://app.warp.dev/login
3. 在 Network 标签页中过滤 `identitytoolkit`
4. 输入一个邮箱尝试登录
5. 查看发送到 `identitytoolkit.googleapis.com` 的请求
6. 从 URL 参数中提取 `key=` 后面的 API Key

示例 URL:
```
https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key=新的APIKey
```

### 方案 2: 从 Warp 桌面客户端提取

如果你安装了 Warp 桌面客户端:

#### Windows:
1. 找到 Warp 安装目录 (通常在 `%LOCALAPPDATA%\warp`)
2. 查找包含 `firebase` 或 `AIzaSy` 的文件
3. 可能的文件:
   - `resources/app.asar` (需要 asar 工具解包)
   - JavaScript 配置文件
   - 环境配置文件

#### 使用工具搜索:
```bash
# 在 Warp 安装目录搜索
findstr /s /i "AIzaSy" *.*
# 或
grep -r "AIzaSy" .
```

### 方案 3: 反编译 Warp 客户端

使用工具如:
- `asar extract` - 解包 Electron 应用
- Chrome DevTools - 调试 Electron 应用
- Wireshark - 抓包分析网络请求

### 方案 4: 使用社区分享的 Key

搜索 GitHub、Reddit 等社区，可能有人分享过有效的 Firebase API Key。

## 更新 API Key

获取到新的 API Key 后，修改以下文件：

1. `config.py`:
```python
FIREBASE_API_KEY = "你的新APIKey"
FIREBASE_API_KEYS = [
    "你的新APIKey1",
    "你的新APIKey2",  # 可选的备用 Key
]
```

2. 重新运行注册脚本测试:
```bash
python test_register/manual_register.py
```

## 临时解决方案

如果无法获取新的 API Key，可以考虑：

1. **使用已有账号池** - 如果数据库中已有账号，可以直接使用
2. **手动注册** - 通过 Warp 官网手动注册账号，然后手动导入到数据库
3. **寻找替代方案** - 寻找其他 AI 服务的 API

## 注意事项

⚠️ **重要提示：**
- 不要在公共场所分享你的 Firebase API Key
- 频繁使用可能导致 Key 被封禁
- 建议准备多个备用 Key
- 定期检查 Key 的有效性
