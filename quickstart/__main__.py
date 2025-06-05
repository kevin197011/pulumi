"""A Kubernetes Python Pulumi program"""

"""Main entry for Pulumi stack."""

import pulumi

from components import nginx, cert_manager, rancher

# Deploy Nginx
nginx_deployment, nginx_namespace = nginx.deploy()

# Deploy Cert-Manager
cert_manager_release, cert_manager_namespace = cert_manager.deploy()

# Deploy Rancher, depends on cert-manager
rancher_release = rancher.deploy(cert_manager_release)

# Outputs
pulumi.export("name", nginx_deployment.metadata["name"])
pulumi.export("namespace", nginx_deployment.metadata["namespace"])

pulumi.export("nginx_namespace", nginx_namespace.metadata["name"])

pulumi.export("cert_manager_release_name", cert_manager_release.name)
pulumi.export("cert_manager_namespace", cert_manager_namespace.metadata["name"])

pulumi.export("rancher_release_name", rancher_release.name)
pulumi.export("rancher_namespace", "cattle-system")  # 你创建 namespace 时已指定
pulumi.export("rancher_hostname", "rancher.local")   # 你在 values 中设置的值
