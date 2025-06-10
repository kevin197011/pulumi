# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""Base component class for Pulumi resources."""

from typing import Any, Dict, Optional, Tuple, Union
import pulumi
import pulumi_kubernetes.core.v1 as core
from pulumi_kubernetes.core.v1 import Namespace
from pulumi_kubernetes.helm.v3 import Release
from pulumi_kubernetes.apps.v1 import Deployment

# 定义资源类型联合
PulumiResource = Union[Release, Deployment, Any]

class BaseComponent:
    """Base class for all Kubernetes components."""

    def __init__(self, name: str, namespace: Optional[str] = None) -> None:
        """Initialize base component.

        Args:
            name: Name of the component
            namespace: Optional namespace name, if None will use component name
        """
        self.name: str = name
        self.namespace_name: str = namespace or name
        self._namespace: Optional[Namespace] = None
        self._resource: Optional[PulumiResource] = None

    def create_namespace(self, **kwargs: Dict[str, Any]) -> Namespace:
        """Create a namespace for the component.

        Args:
            **kwargs: Additional arguments to pass to Namespace creation

        Returns:
            Created namespace resource
        """
        self._namespace = core.Namespace(
            self.namespace_name,
            metadata={"name": self.namespace_name},
            opts=pulumi.ResourceOptions(
                additional_secret_outputs=["metadata.name"],
                **kwargs.get("opts", {})
            )
        )
        return self._namespace

    @property
    def namespace(self) -> Namespace:
        """Get the namespace resource.

        Returns:
            The namespace resource, creating it if it doesn't exist
        """
        if not self._namespace:
            self._namespace = self.create_namespace()
        return self._namespace

    @property
    def resource(self) -> Optional[PulumiResource]:
        """Get the main resource of the component.

        Returns:
            The main resource of the component, if it exists
        """
        return self._resource

    def deploy(self, **kwargs: Dict[str, Any]) -> Tuple[PulumiResource, Namespace]:
        """Deploy the component. Must be implemented by subclasses.

        Args:
            **kwargs: Deployment configuration parameters

        Returns:
            Tuple of (deployed resource, namespace)

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement deploy()")