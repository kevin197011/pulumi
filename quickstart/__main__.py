# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""A Kubernetes Python Pulumi program"""

"""Main entry for Pulumi stack."""

from typing import Dict, Any
import pulumi
from pulumi_kubernetes.apps.v1 import Deployment
from pulumi_kubernetes.core.v1 import Namespace
from pulumi_kubernetes.helm.v3 import Release
from components.nginx import NginxComponent
from components.cert_manager import CertManagerComponent
from components.rancher import RancherComponent
from components.ingress import IngressComponent

# Initialize components
nginx_component: NginxComponent = NginxComponent(name="nginx")
cert_manager_component: CertManagerComponent = CertManagerComponent(name="cert-manager")
ingress_component: IngressComponent = IngressComponent(name="ingress-nginx")
rancher_component: RancherComponent = RancherComponent(name="rancher", namespace="cattle-system")

# Deploy Nginx
nginx_deployment: Deployment
nginx_namespace: Namespace
nginx_deployment, nginx_namespace = nginx_component.deploy(
    replicas=1,
    image="nginx:latest"
)

# Deploy NGINX Ingress Controller
ingress_release: Release
ingress_namespace: Namespace
ingress_release, ingress_namespace = ingress_component.deploy(
    version="4.9.1",
    controller_replicas=1,
    enable_metrics=False,  # 禁用 Prometheus 指标
    service_type="LoadBalancer",
    default_tls=True
)

# Deploy Cert-Manager
cert_manager_release: Release
cert_manager_namespace: Namespace
cert_manager_release, cert_manager_namespace = cert_manager_component.deploy(
    version="v1.17.2"
)

# Deploy Rancher with Ingress
rancher_release: Release
rancher_namespace: Namespace
rancher_release, rancher_namespace = rancher_component.deploy(
    depends_on_release=[cert_manager_release, ingress_release],
    version="2.11.2",
    hostname="rancher.local",
    replicas=1,
    ingress_class="nginx",
    tls_source="rancher",
    bootstrap_password="admin123"
)

# Export outputs with type annotations
nginx_output: Dict[str, Any] = {
    "name": nginx_deployment.metadata["name"],
    "namespace": nginx_namespace.metadata["name"],
    "deployment_namespace": nginx_deployment.metadata["namespace"]
}

ingress_output: Dict[str, Any] = {
    "release_name": ingress_release.name,
    "namespace": ingress_namespace.metadata["name"],
    "service_type": "LoadBalancer",
    "metrics_enabled": False
}

cert_manager_output: Dict[str, Any] = {
    "release_name": cert_manager_release.name,
    "namespace": cert_manager_namespace.metadata["name"]
}

rancher_output: Dict[str, Any] = {
    "release_name": rancher_release.name,
    "namespace": rancher_namespace.metadata["name"],
    "hostname": "rancher.local",
    "ingress_enabled": True,
    "tls_source": "rancher"
}

# Export the outputs
pulumi.export("nginx", nginx_output)
pulumi.export("ingress", ingress_output)
pulumi.export("cert_manager", cert_manager_output)
pulumi.export("rancher", rancher_output)
