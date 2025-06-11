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
                ingress_class: Ingress class name (default: nginx)
                tls_source: TLS source, one of: rancher, letsEncrypt, secret (default: rancher)
                acme_email: Email for Let's Encrypt (required if tls_source is letsEncrypt)
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

        # 基本配置
        values: Dict[str, Any] = {
            "replicas": kwargs.get("replicas", 1),
            "hostname": kwargs.get("hostname", "rancher.local"),
            "ingress": {
                "enabled": True,
                "extraAnnotations": {
                    "kubernetes.io/ingress.class": kwargs.get("ingress_class", "nginx"),
                    "cert-manager.io/cluster-issuer": "rancher-selfsigned",
                },
                "tls": {
                    "source": kwargs.get("tls_source", "rancher")
                }
            },
            "bootstrapPassword": kwargs.get("bootstrap_password", "admin123"),
        }

        # TLS 配置
        tls_source: str = kwargs.get("tls_source", "rancher")
        if tls_source == "letsEncrypt":
            acme_email = kwargs.get("acme_email")
            if not acme_email:
                raise ValueError("acme_email is required when using Let's Encrypt")
            values["ingress"]["extraAnnotations"].update({
                "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                "acme.cert-manager.io/http01-edit-in-place": "true"
            })
            values["ingress"]["tls"] = {
                "source": "letsEncrypt",
                "acme": {
                    "email": acme_email
                }
            }
        elif tls_source == "secret":
            values["ingress"]["tls"] = {
                "source": "secret",
                "secretName": kwargs.get("tls_secret_name", f"{self.name}-tls")
            }

        # 合并用户提供的额外配置
        if "values" in kwargs:
            values.update(kwargs["values"])

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
