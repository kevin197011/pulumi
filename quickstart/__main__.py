"""A Kubernetes Python Pulumi program"""

"""Main entry for Pulumi stack."""

import pulumi
from components.nginx import NginxComponent
from components.cert_manager import CertManagerComponent
from components.rancher import RancherComponent

# Initialize components
nginx_component = NginxComponent(name="nginx")
cert_manager_component = CertManagerComponent(name="cert-manager")
rancher_component = RancherComponent(name="rancher", namespace="cattle-system")

# Deploy Nginx
nginx_deployment, nginx_namespace = nginx_component.deploy(
    replicas=1,
    image="nginx:latest"
)

# Deploy Cert-Manager
cert_manager_release, cert_manager_namespace = cert_manager_component.deploy(
    version="v1.17.2"
)

# Deploy Rancher, depends on cert-manager
rancher_release, rancher_namespace = rancher_component.deploy(
    depends_on_release=cert_manager_release,
    version="2.11.2",
    hostname="rancher.local",
    replicas=1,
    ingress_enabled=False,
    service_type="NodePort",
    node_port=31000,
    bootstrap_password="admin123"
)

# Export outputs
pulumi.export("nginx", {
    "name": nginx_deployment.metadata["name"],
    "namespace": nginx_namespace.metadata["name"],
    "deployment_namespace": nginx_deployment.metadata["namespace"]
})

pulumi.export("cert_manager", {
    "release_name": cert_manager_release.name,
    "namespace": cert_manager_namespace.metadata["name"]
})

pulumi.export("rancher", {
    "release_name": rancher_release.name,
    "namespace": rancher_namespace.metadata["name"],
    "hostname": "rancher.local"
})
