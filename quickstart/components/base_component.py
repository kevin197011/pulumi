"""Base component class for Pulumi resources."""

import pulumi
import pulumi_kubernetes.core.v1 as core

class BaseComponent:
    """Base class for all Kubernetes components."""

    def __init__(self, name: str, namespace: str = None):
        """Initialize base component.

        Args:
            name: Name of the component
            namespace: Optional namespace name, if None will use component name
        """
        self.name = name
        self.namespace_name = namespace or name
        self._namespace = None
        self._resource = None

    def create_namespace(self, **kwargs) -> core.Namespace:
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
    def namespace(self) -> core.Namespace:
        """Get the namespace resource."""
        if not self._namespace:
            self._namespace = self.create_namespace()
        return self._namespace

    @property
    def resource(self):
        """Get the main resource of the component."""
        return self._resource

    def deploy(self, **kwargs):
        """Deploy the component. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement deploy()")