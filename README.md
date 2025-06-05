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
│   │   ├── cert_manager.py
│   │   ├── nginx.py
│   │   └── rancher.py
│   ├── __main__.py
│   ├── deploy.sh
│   └── pyproject.toml
```

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

This will:
1. Deploy NGINX with health checks and resource limits
2. Install cert-manager with CRDs for certificate management
3. Deploy Rancher with NodePort access

## Configuration

Key configurations:

- NGINX:
  - Image: nginx:latest
  - Resources: 100m-200m CPU, 128Mi-256Mi Memory
  - Health checks on port 80

- Cert Manager:
  - Version: v1.14.4
  - Custom resource definitions enabled

- Rancher:
  - Version: 2.11.2
  - NodePort: 31000
  - Hostname: rancher.local
  - Default admin password: admin123

## License

MIT License - See [LICENSE](LICENSE) for details
