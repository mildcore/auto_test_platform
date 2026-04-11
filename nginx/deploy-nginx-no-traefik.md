# 自动化测试平台 - 宿主机 Nginx 部署指南

本指南适用于 **VPS 已有 Nginx 服务** 的场景，使用宿主机 Nginx 统一处理 SSL 和反向代理，去掉 Traefik 以节省资源。

## 架构说明

```
用户 ──HTTPS──► 宿主机 Nginx(443) ──HTTP──► 前端容器(80)
                                                  ↓
                                           前端容器内 Nginx
                                                  ↓
                                           后端容器(5000)
```

**特点：**
- SSL 统一在宿主机 Nginx 处理（acme.sh 管理证书）
- 前端容器内 Nginx 代理 `/api/` 请求到后端
- 后端不暴露端口，仅内部容器通信
- 无 Traefik，节省约 100MB+ 内存

---

## 前置要求

1. **已安装 Docker 和 Docker Compose**
2. **已有 Nginx 服务** 监听 80/443 端口
3. **已安装 acme.sh** 用于 SSL 证书管理
4. **域名已解析** 到 VPS IP

---

## 部署步骤

### 1. 申请 SSL 证书

使用 acme.sh 为域名申请证书：

```bash
# 申请证书（根据你的 DNS 提供商调整, example.com更改为实际的域名）
acme.sh --issue --dns dns_ali -d example.com

# 安装证书到 Nginx 目录
acme.sh --install-cert -d example.com \
  --key-file /etc/nginx/ssl/example.com/key.pem \
  --fullchain-file /etc/nginx/ssl/example.com/fullchain.pem \
  --reloadcmd "systemctl reload nginx"
```

**注意**：确保 `/etc/nginx/ssl/example.com/` 目录存在。

---

### 2. 配置环境变量

在项目根目录 `sudo cp .env.example .env` 并根据实际修改

---

### 3. 配置宿主机 Nginx

复制示例配置并修改：

```bash
sudo cp nginx/atp.conf.example /etc/nginx/conf.d/atp.conf

# 使用 sed 一键替换域名（将 example.com 替换为你的实际域名）
sudo sed -i 's/example.com/your-domain.com/g' /etc/nginx/conf.d/atp.conf

# 或者使用 vim 编辑
# sudo vim /etc/nginx/conf.d/atp.conf
```

**修改内容：**
- 将 `example.com` 替换为实际域名，:%s/example.com/your-domain.com/g
- 确认 SSL 证书路径正确
- 确认代理端口 `3000` 与 docker-compose 中的一致

**测试并重载 Nginx：**

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

### 4. 修改前端配置（可选但建议）

建议修改前端 `nginx.conf` 中的 `server_name` 以更加规范：

```nginx
# frontend/nginx.conf
server {
    listen 80;
    server_name _;  # 改为通配符，或删除此行
    # ...
}
```

修改后需要重新构建镜像：

```bash
docker compose -f docker-compose.yml -f docker-compose.vps-no-traefik.yml build frontend
```

---

### 5. 启动服务

```bash
# 进入项目目录
cd /path/to/auto_test_platform

# 启动所有服务
docker compose -f docker-compose.yml -f docker-compose.vps-no-traefik.yml up -d
```

**检查状态：**

```bash
docker compose ps
docker compose logs -f
```

---

### 6. 验证部署

1. **访问网站**：https://example.com
2. **检查 SSL**：浏览器应显示证书有效
3. **测试 API**：尝试登录或查看数据，确认前后端通信正常

---

## 常用命令

### 查看日志

```bash
# 查看所有服务日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f frontend
docker compose logs -f backend
docker compose logs -f celery-worker
```

### 重启服务

```bash
# 重启所有服务
docker compose restart

# 重启单个服务
docker compose restart frontend
```

### 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker compose -f docker-compose.yml -f docker-compose.vps-no-traefik.yml up -d --build
```

### 停止服务

```bash
docker compose -f docker-compose.yml -f docker-compose.vps-no-traefik.yml down
```

### 备份数据库

```bash
# 创建备份
docker compose exec db mysqldump -u root -p auto_test > backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## 故障排查

### 1. 网站无法访问

检查步骤：

```bash
# 1. 检查容器状态
docker compose ps

# 2. 检查前端是否在监听 3000 端口
ss -tlnp | grep 3000

# 3. 测试本地访问
curl -H "Host: example.com" http://127.0.0.1:3000

# 4. 检查 Nginx 错误日志
sudo tail -f /var/log/nginx/example.com-error.log
```

### 2. API 请求 502 错误

可能是后端服务异常：

```bash
# 检查后端日志
docker compose logs backend

# 检查数据库连接
docker compose exec backend python -c "from app import db; db.engine.connect()"
```

### 3. SSL 证书问题

```bash
# 检查证书有效期
openssl x509 -in /etc/nginx/ssl/example.com/fullchain.pem -noout -dates

# 手动续期测试
acme.sh --renew -d example.com --force
```

### 4. 内存不足（OOM）

VPS 内存不足时，可进一步限制资源：

```yaml
# docker-compose.vps-no-traefik.yml
deploy:
  resources:
    limits:
      cpus: '0.2'      # 降低 CPU 限制
      memory: 96M      # 降低内存限制
```

---

## 与带 Traefik 方案对比

| 项目 | 宿主机 Nginx | Traefik |
|------|-------------|---------|
| **内存占用** | 更低（无 Traefik） | 高 100MB+ |
| **SSL 管理** | acme.sh 统一 | Let's Encrypt 自动 |
| **配置复杂度** | 需手动配 Nginx | 自动发现，标签配置 |
| **适用场景** | 已有 Nginx 的 VPS | 新环境/多域名管理 |
| **动态扩展** | 需手动改配置 | 自动发现新容器 |

---

## 文件说明

```
auto_test_platform/
├── docker-compose.yml              # 基础配置（服务定义）
├── docker-compose.vps-no-traefik.yml  # VPS 无 Traefik 配置（资源限制、端口映射）
├── nginx/
│   └── atp.conf.example            # Nginx 配置模板
├── deploy-nginx-no-traefik.md      # 本部署文档
└── .env                            # 环境变量（需自行创建）
```

---

## 注意事项

1. **端口占用**：确保 `127.0.0.1:3000` 未被其他服务占用
2. **防火墙**：确保 80/443 端口开放
3. **证书续期**：acme.sh 会自动续期，但建议定期检查
4. **备份**：定期备份数据库和重要数据
5. **安全**：不要将 `.env` 文件提交到 Git

---

## 参考链接

- [acme.sh 文档](https://github.com/acmesh-official/acme.sh/wiki)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Nginx 代理文档](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
