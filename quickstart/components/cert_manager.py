# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from typing import Dict, Optional, Tuple, Any
import pulumi_kubernetes.helm.v3 as helm
from pulumi_kubernetes.core.v1 import Namespace
from .base_component import BaseComponent

class CertManagerComponent(BaseComponent):
    """Cert Manager deployment component."""

    def __init__(self, name: str = "cert-manager", namespace: Optional[str] = None) -> None:
        """Initialize Cert Manager component.

        Args:
            name: Name of the component (default: cert-manager)
            namespace: Optional namespace name
        """
        super().__init__(name, namespace)

    def deploy(self, **kwargs: Dict[str, Any]) -> Tuple[helm.Release, Namespace]:
        """Deploy Cert Manager component.

        Args:
            **kwargs: Additional deployment configuration
                version: Chart version (default: v1.17.2)
                repository: Chart repository URL
                values: Additional Helm values
                install_crds: Whether to install CRDs (default: True)

        Returns:
            tuple: (release, namespace)
        """
        chart_version: str = kwargs.get("version", "v1.17.2")
        repository: str = kwargs.get("repository", "https://charts.jetstack.io")
        values: Dict[str, Any] = {
            "installCRDs": kwargs.get("install_crds", True),
            **(kwargs.get("values", {}))
        }

        release: helm.Release = helm.Release(
            self.name,
            helm.ReleaseArgs(
                chart="cert-manager",
                version=chart_version,
                namespace=self.namespace.metadata["name"],
                create_namespace=True,
                repository_opts=helm.RepositoryOptsArgs(
                    repo=repository
                ),
                values=values,
            )
        )
        self._resource = release
        return release, self.namespace
