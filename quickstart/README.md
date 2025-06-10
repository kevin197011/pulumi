# Pulumi Infrastructure as Code

基于 Pulumi 的 Kubernetes 基础设施即代码项目，采用面向对象设计模式实现以下组件的自动化部署：

- NGINX Web 服务器
- Cert Manager 证书管理
- Rancher Kubernetes 集群管理

## 环境要求

### 必需组件
- Python 3.x
- Pulumi CLI
- kubectl 已配置的 Kubernetes 集群访问
- pip 或 uv 包管理器

### 推荐工具
- Visual Studio Code
- Python 插件
- Kubernetes 插件
- Pulumi 插件

## 项目结构

```
.
├── quickstart/
│   ├── components/                # 组件目录
│   │   ├── __init__.py
│   │   ├── base_component.py     # 基础组件类
│   │   ├── cert_manager.py       # 证书管理组件
│   │   ├── nginx.py             # NGINX组件
│   │   └── rancher.py           # Rancher组件
│   ├── __main__.py              # 主部署脚本
│   ├── deploy.sh                # 部署脚本
│   └── pyproject.toml           # 项目依赖配置
```

## 组件架构

采用面向对象设计模式，实现了一个灵活可扩展的组件架构：

### 基础组件 (BaseComponent)
```python
class BaseComponent:
    def __init__(self, name: str, namespace: str = None)
    def create_namespace(self) -> Namespace
    def deploy(self, **kwargs)
```

- 命名空间管理
- 资源追踪
- 标准化部署接口
- 错误处理机制

### 具体组件实现
- `NginxComponent`: NGINX Web服务器部署
- `CertManagerComponent`: SSL/TLS证书管理
- `RancherComponent`: Kubernetes集群管理平台

## 快速开始

### 1. 安装依赖

```bash
# 使用 pip 安装
pip install -r requirements.txt

# 或使用 uv 安装（推荐，更快）
uv pip install -r requirements.txt
```

### 2. 配置 Pulumi

```bash
# 设置本地状态存储
export PULUMI_BACKEND_URL=file://$(pwd)/state
export PULUMI_CONFIG_PASSPHRASE="123456"
pulumi login $PULUMI_BACKEND_URL

# 创建新的 stack（如果需要）
pulumi stack init dev
```

### 3. 部署基础设施

```bash
# 使用部署脚本
cd quickstart
./deploy.sh

# 或直接使用 Pulumi 命令
pulumi up
```

## 组件配置指南

### NGINX 组件
```python
nginx = NginxComponent(name="nginx", namespace="nginx")
deployment, ns = nginx.deploy(
    replicas=1,
    image="nginx:latest",
    # 更多配置选项...
)
```

配置参数：
- `replicas`: 副本数量
- `image`: 容器镜像
- 资源限制：
  - 请求：CPU 100m，内存 128Mi
  - 限制：CPU 200m，内存 256Mi
- 健康检查：
  - 存活探针：端口 80，路径 /
  - 就绪探针：端口 80，路径 /

### Cert Manager 组件
```python
cert_manager = CertManagerComponent(name="cert-manager")
release, ns = cert_manager.deploy(
    version="v1.17.2",
    # 更多配置选项...
)
```

配置参数：
- `version`: 组件版本
- `repository`: charts 仓库地址
- `values`: Helm values 配置
- CRDs: 自动安装和管理

### Rancher 组件
```python
rancher = RancherComponent(name="rancher", namespace="cattle-system")
release, ns = rancher.deploy(
    depends_on_release=cert_manager_release,
    version="2.11.2",
    hostname="rancher.local",
    # 更多配置选项...
)
```

配置参数：
- `version`: Rancher 版本
- `hostname`: 访问域名
- `service`: 服务配置
  - 类型：NodePort
  - 端口：31000
- 默认配置：
  - 管理员密码：admin123
  - Ingress：默认禁用

## 输出信息

部署完成后会输出以下信息：

```yaml
nginx:
  name: nginx
  namespace: nginx
  deployment_namespace: nginx

cert_manager:
  release_name: cert-manager
  namespace: cert-manager

rancher:
  release_name: rancher
  namespace: cattle-system
  hostname: rancher.local
```

## 开发指南

### 添加新组件

1. 创建新的组件类文件
2. 继承 `BaseComponent` 类
3. 实现 `deploy` 方法
4. 在 `__main__.py` 中使用新组件

示例：
```python
from .base_component import BaseComponent

class NewComponent(BaseComponent):
    def deploy(self, **kwargs):
        # 实现部署逻辑
        return resource, namespace
```

### 最佳实践

- 使用类型注解
- 添加详细文档字符串
- 实现适当的错误处理
- 保持配置的灵活性
- 遵循 Python 编码规范

## 故障排除

常见问题：

1. 命名空间已存在
   ```bash
   kubectl delete namespace <namespace>
   ```

2. 端口冲突
   ```bash
   # 检查端口占用
   netstat -tulpn | grep <port>
   ```

3. 证书问题
   ```bash
   # 检查证书状态
   kubectl get certificates -A
   ```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件