# GitHub OAuth 配置说明

## 如何配置 GitHub OAuth 应用

### 场景 1: 本地开发（应用运行在本地）
如果您在本地机器上运行应用，使用 `localhost`：

```
Application name: Code Agent Dev
Homepage URL: http://localhost:8080
Authorization callback URL: http://localhost:8080/api/v1/github/callback
```

### 场景 2: 云端开发/远程服务器（推荐）
如果应用运行在云端或远程服务器（如本环境），**必须使用实际的服务器地址**：

#### 方案 A: 使用服务器 IP 地址
```
Application name: Code Agent Cloud
Homepage URL: http://<服务器IP>:8080
Authorization callback URL: http://<服务器IP>:8080/api/v1/github/callback
```

例如（根据当前环境）：
```
Homepage URL: http://172.20.148.1:8080
Authorization callback URL: http://172.20.148.1:8080/api/v1/github/callback
```

#### 方案 B: 使用域名（如果有）
如果有绑定的域名：
```
Homepage URL: https://yourdomain.com
Authorization callback URL: https://yourdomain.com/api/v1/github/callback
```

### 场景 3: Docker 容器部署
如果使用 Docker 部署，需要确保端口映射正确：

```bash
# 确保端口 8080 已映射到主机
docker run -p 8080:8080 your-app
```

然后使用主机的 IP 或域名（不是容器内部的 localhost）。

## 配置 .env 文件

创建 GitHub OAuth App 后，将获取的凭证填入 `.env` 文件：

```bash
# GitHub OAuth 设置
GITHUB_CLIENT_ID=ghp_xxxxxxxxxxxxxxxxxxxxxxxx  # 替换为实际的 Client ID
GITHUB_CLIENT_secret=ghp_xxxxxxxxxxxxxxxxxxxxxxxx  # 替换为实际的 Client Secret

# 回调 URL 必须与 GitHub OAuth App 中配置的完全一致
GITHUB_REDIRECT_URI=http://<服务器IP>:8080/api/v1/github/callback
```

## 创建 GitHub OAuth App 的步骤

1. 访问 [GitHub Developer Settings](https://github.com/settings/developers)
2. 点击左侧菜单的 "OAuth Apps" → "New OAuth App"
3. 填写表单：
   - **Application name**: 任意名称（如 "Code Agent"）
   - **Homepage URL**: 根据上述场景填写
   - **Application description**: 可选
   - **Authorization callback URL**: `http://<地址>:8080/api/v1/github/callback`
4. 点击 "Register application"
5. 复制显示的 **Client ID**
6. 点击 "Generate a new client Secret"
7. 复制显示的 **Client Secret**（只显示一次，请妥善保存）

## 重要提示

### ⚠️ 回调 URL 必须完全匹配
GitHub OAuth App 中配置的回调 URL 必须与 `.env` 文件中的 `GITHUB_REDIRECT_URI` **完全一致**，包括：
- 协议（http 或 https）
- 域名或 IP
- 端口号
- 路径

### ⚠️ localhost vs IP 地址
- **localhost** 只能从本地机器访问
- **IP 地址** 可以从网络中的任何机器访问
- 在云端/容器环境中，必须使用外部可访问的地址

### ⚠️ 端口映射
如果使用 Docker，确保端口已正确映射：
```bash
docker run -p 8080:8080 ...
```

### ⚠️ 防火墙设置
确保服务器防火墙允许 8080 端口的入站连接。

## 测试配置

配置完成后，测试连接：

1. 访问 `http://<地址>:8080`
2. 点击 "连接 GitHub"
3. 应该跳转到 GitHub 授权页面
4. 授权后应该返回到应用并显示成功信息

## 常见问题

### Q: 提示 "Redirect URI mismatch"
**A**: 检查 `.env` 中的 `GITHUB_REDIRECT_URI` 是否与 GitHub OAuth App 中的配置完全一致。

### Q: 授权后没有返回到应用
**A**: 检查服务器端口是否开放，回调 URL 是否可以从外部访问。

### Q: 本地可以，远程不行
**A**: 将 `localhost` 替换为服务器的实际 IP 地址，并重新配置 GitHub OAuth App。

### Q: Docker 中无法访问
**A**: 确保使用宿主机 IP 或域名，不要使用容器内部的 localhost。
