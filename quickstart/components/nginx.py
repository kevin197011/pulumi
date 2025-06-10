# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from pulumi_kubernetes.apps.v1 import Deployment
from .base_component import BaseComponent

class NginxComponent(BaseComponent):
    """Nginx deployment component."""

    def __init__(self, name: str = "nginx", namespace: str = None):
        """Initialize Nginx component.

        Args:
            name: Name of the component (default: nginx)
            namespace: Optional namespace name
        """
        super().__init__(name, namespace)
        self.app_labels = {"app": self.name}

    def deploy(self, **kwargs):
        """Deploy Nginx component.

        Args:
            **kwargs: Additional deployment configuration

        Returns:
            tuple: (deployment, namespace)
        """
        deployment = Deployment(
            self.name,
            metadata={"namespace": self.namespace.metadata["name"]},
            spec={
                "selector": {"match_labels": self.app_labels},
                "replicas": kwargs.get("replicas", 1),
                "template": {
                    "metadata": {"labels": self.app_labels},
                    "spec": {
                        "containers": [{
                            "name": self.name,
                            "image": kwargs.get("image", "nginx:latest"),
                            "ports": [{"container_port": 80}],
                            "resources": {
                                "requests": {"cpu": "100m", "memory": "128Mi"},
                                "limits": {"cpu": "200m", "memory": "256Mi"},
                            },
                            "liveness_probe": {
                                "http_get": {"path": "/", "port": 80},
                                "initial_delay_seconds": 30,
                                "timeout_seconds": 5,
                            },
                            "readiness_probe": {
                                "http_get": {"path": "/", "port": 80},
                                "initial_delay_seconds": 5,
                                "timeout_seconds": 5,
                            },
                        }],
                        "restart_policy": "Always",
                    },
                },
            },
        )
        self._resource = deployment
        return deployment, self.namespace
