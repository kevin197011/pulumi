# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import pulumi_kubernetes.helm.v3 as helm
from .base_component import BaseComponent

class CertManagerComponent(BaseComponent):
    """Cert Manager deployment component."""

    def __init__(self, name: str = "cert-manager", namespace: str = None):
        """Initialize Cert Manager component.

        Args:
            name: Name of the component (default: cert-manager)
            namespace: Optional namespace name
        """
        super().__init__(name, namespace)

    def deploy(self, **kwargs):
        """Deploy Cert Manager component.

        Args:
            **kwargs: Additional deployment configuration

        Returns:
            tuple: (release, namespace)
        """
        release = helm.Release(
            self.name,
            helm.ReleaseArgs(
                chart="cert-manager",
                version=kwargs.get("version", "v1.14.4"),
                namespace=self.namespace.metadata["name"],
                create_namespace=True,
                repository_opts=helm.RepositoryOptsArgs(
                    repo="https://charts.jetstack.io"
                ),
                values={"installCRDs": True},
            )
        )
        self._resource = release
        return release, self.namespace
