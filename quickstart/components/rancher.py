# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import pulumi
import pulumi_kubernetes.helm.v3 as helm
from .base_component import BaseComponent

class RancherComponent(BaseComponent):
    """Rancher deployment component."""

    def __init__(self, name: str = "rancher", namespace: str = "cattle-system"):
        """Initialize Rancher component.

        Args:
            name: Name of the component (default: rancher)
            namespace: Namespace name (default: cattle-system)
        """
        super().__init__(name, namespace)

    def deploy(self, depends_on_release=None, **kwargs):
        """Deploy Rancher component.

        Args:
            depends_on_release: Optional release dependency
            **kwargs: Additional deployment configuration

        Returns:
            tuple: (release, namespace)
        """
        release = helm.Release(
            self.name,
            helm.ReleaseArgs(
                chart="rancher",
                version=kwargs.get("version", "2.11.2"),
                namespace=self.namespace.metadata["name"],
                repository_opts=helm.RepositoryOptsArgs(
                    repo="https://releases.rancher.com/server-charts/stable"
                ),
                values={
                    "replicas": kwargs.get("replicas", 1),
                    "hostname": kwargs.get("hostname", "rancher.local"),
                    "ingress": {"enabled": kwargs.get("ingress_enabled", False)},
                    "service": {
                        "type": kwargs.get("service_type", "NodePort"),
                        "nodePort": kwargs.get("node_port", 31000)
                    },
                    "bootstrapPassword": kwargs.get("bootstrap_password", "admin123")
                },
            ),
            opts=pulumi.ResourceOptions(depends_on=[depends_on_release] if depends_on_release else None)
        )
        self._resource = release
        return release, self.namespace
