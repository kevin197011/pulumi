# Pulumi Infrastructure as Code

This project uses Pulumi to deploy a Kubernetes infrastructure with the following components:

- NGINX web server
- Cert Manager for SSL/TLS certificate management
- Rancher for Kubernetes cluster management

## Prerequisites

- Python 3.x
- Pulumi CLI
- Kubernetes cluster access configured
- `pip` or `uv` package manager

## Project Structure

```
.
├── quickstart/
│   ├── components/
│   │   ├── __init__.py
│   │   ├── base_component.py    # Base class for all components
│   │   ├── cert_manager.py      # Cert Manager component
│   │   ├── nginx.py            # NGINX component
│   │   └── rancher.py          # Rancher component
│   ├── __main__.py             # Main deployment script
│   ├── deploy.sh
│   └── pyproject.toml
```

## Component Architecture

The project follows an Object-Oriented design pattern:

- `BaseComponent`: Abstract base class providing common functionality
  - Namespace management
  - Resource tracking
  - Standardized deployment interface

- Concrete Components:
  - `NginxComponent`: NGINX deployment
  - `CertManagerComponent`: Certificate management
  - `RancherComponent`: Rancher deployment

## Installation

1. Install Python dependencies:

```sh
# Using pip
pip install -r requirements.txt

# Or using uv
uv pip install -r requirements.txt
```

2. Configure Pulumi:

```sh
export PULUMI_BACKEND_URL=file://$(pwd)/state
export PULUMI_CONFIG_PASSPHRASE="123456"
pulumi login $PULUMI_BACKEND_URL
```

## Deployment

Run the deployment script:

```sh
cd quickstart
./deploy.sh
```

Or deploy manually:

```python
# Example deployment code
from components.nginx import NginxComponent
from components.cert_manager import CertManagerComponent
from components.rancher import RancherComponent

# Initialize components
nginx = NginxComponent()
cert_manager = CertManagerComponent()
rancher = RancherComponent()

# Deploy
nginx_deployment, nginx_ns = nginx.deploy(replicas=1)
cert_manager_release, cert_manager_ns = cert_manager.deploy()
rancher_release, rancher_ns = rancher.deploy(depends_on_release=cert_manager_release)
```

## Configuration

### NGINX Component
```python
NginxComponent(name="nginx", namespace=None)
```
- Image: nginx:latest
- Resources:
  - Requests: 100m CPU, 128Mi Memory
  - Limits: 200m CPU, 256Mi Memory
- Health checks:
  - Liveness: Port 80, Path /
  - Readiness: Port 80, Path /

### Cert Manager Component
```python
CertManagerComponent(name="cert-manager", namespace=None)
```
- Version: v1.17.2
- Repository: https://charts.jetstack.io
- CRDs: Automatically installed

### Rancher Component
```python
RancherComponent(name="rancher", namespace="cattle-system")
```
- Version: 2.11.2
- Repository: https://releases.rancher.com/server-charts/stable
- Service:
  - Type: NodePort
  - Port: 31000
- Default Settings:
  - Hostname: rancher.local
  - Bootstrap Password: admin123
  - Ingress: Disabled by default

## Outputs

The deployment exports structured outputs:

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

## License

MIT License - See [LICENSE](LICENSE) for details