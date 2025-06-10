# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from typing import Dict, Optional, Tuple, Any, Union
import pulumi
import pulumi_kubernetes.helm.v3 as helm
from pulumi_kubernetes.core.v1 import Namespace
from .base_component import BaseComponent

class RancherComponent(BaseComponent):
    """Rancher deployment component."""

    def __init__(self, name: str = "rancher", namespace: str = "cattle-system") -> None:
        """Initialize Rancher component.

        Args:
            name: Name of the component (default: rancher)
            namespace: Namespace name (default: cattle-system)
        """
        super().__init__(name, namespace)

    def deploy(
        self,
        depends_on_release: Optional[Union[helm.Release, Any]] = None,
        **kwargs: Dict[str, Any]
    ) -> Tuple[helm.Release, Namespace]:
        """Deploy Rancher component.

        Args:
            depends_on_release: Optional release dependency
            **kwargs: Additional deployment configuration
                version: Chart version (default: 2.11.2)
                hostname: Rancher hostname (default: rancher.local)
                replicas: Number of replicas (default: 1)
                ingress_enabled: Enable ingress (default: False)
                service_type: Service type (default: NodePort)
                node_port: NodePort number (default: 31000)
                bootstrap_password: Admin password (default: admin123)
                repository: Chart repository URL
                values: Additional Helm values

        Returns:
            tuple: (release, namespace)
        """
        chart_version: str = kwargs.get("version", "2.11.2")
        repository: str = kwargs.get(
            "repository",
            "https://releases.rancher.com/server-charts/stable"
        )

        values: Dict[str, Any] = {
            "replicas": kwargs.get("replicas", 1),
            "hostname": kwargs.get("hostname", "rancher.local"),
            "ingress": {
                "enabled": kwargs.get("ingress_enabled", False)
            },
            "service": {
                "type": kwargs.get("service_type", "NodePort"),
                "nodePort": kwargs.get("node_port", 31000)
            },
            "bootstrapPassword": kwargs.get("bootstrap_password", "admin123"),
            **(kwargs.get("values", {}))
        }

        release: helm.Release = helm.Release(
            self.name,
            helm.ReleaseArgs(
                chart="rancher",
                version=chart_version,
                namespace=self.namespace.metadata["name"],
                repository_opts=helm.RepositoryOptsArgs(
                    repo=repository
                ),
                values=values,
            ),
            opts=pulumi.ResourceOptions(
                depends_on=[depends_on_release] if depends_on_release else None
            )
        )
        self._resource = release
        return release, self.namespace
