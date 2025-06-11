# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from typing import Dict, Optional, Tuple, Any
import pulumi
import pulumi_kubernetes.helm.v3 as helm
from pulumi_kubernetes.core.v1 import Namespace
from .base_component import BaseComponent

class IngressComponent(BaseComponent):
    """NGINX Ingress Controller deployment component."""

    def __init__(self, name: str = "ingress-nginx", namespace: str = "ingress-nginx") -> None:
        """Initialize NGINX Ingress Controller component.

        Args:
            name: Name of the component (default: ingress-nginx)
            namespace: Namespace name (default: ingress-nginx)
        """
        super().__init__(name, namespace)

    def deploy(self, **kwargs: Dict[str, Any]) -> Tuple[helm.Release, Namespace]:
        """Deploy NGINX Ingress Controller component.

        Args:
            **kwargs: Additional deployment configuration
                version: Chart version (default: 4.9.1)
                controller_replicas: Number of replicas (default: 1)
                enable_metrics: Enable Prometheus metrics (default: False)
                default_tls: Enable default TLS certificate (default: True)
                repository: Chart repository URL
                values: Additional Helm values

        Returns:
            tuple: (release, namespace)
        """
        chart_version: str = kwargs.get("version", "4.9.1")
        repository: str = kwargs.get(
            "repository",
            "https://kubernetes.github.io/ingress-nginx"
        )

        # 基本配置
        values: Dict[str, Any] = {
            "controller": {
                "name": "controller",
                "image": {
                    "allowPrivilegeEscalation": False,
                },
                "replicaCount": kwargs.get("controller_replicas", 1),
                "resources": {
                    "requests": {
                        "cpu": "50m",        # 降低 CPU 请求
                        "memory": "90Mi"     # 降低内存请求
                    },
                    "limits": {
                        "cpu": "200m",
                        "memory": "256Mi"
                    }
                },
                "metrics": {
                    "enabled": kwargs.get("enable_metrics", False),
                    "serviceMonitor": {
                        "enabled": False
                    }
                },
                "podSecurityContext": {
                    "runAsUser": 101,
                    "runAsGroup": 101,
                    "runAsNonRoot": True,
                    "fsGroup": 101
                },
                "containerSecurityContext": {
                    "runAsUser": 101,
                    "runAsGroup": 101,
                    "runAsNonRoot": True,
                    "allowPrivilegeEscalation": True,  # 允许权限提升以运行 dumb-init
                    "capabilities": {
                        "drop": ["ALL"],
                        "add": ["NET_BIND_SERVICE"]  # 允许绑定特权端口
                    }
                },
                "config": {
                    "enable-real-ip": "true",
                    "use-forwarded-headers": "true",
                    "compute-full-forwarded-for": "true",
                    "use-proxy-protocol": "false",
                    "proxy-body-size": "50m",
                    "keep-alive": "75",          # 优化连接保持时间
                    "keep-alive-requests": "100", # 每个连接的最大请求数
                    "upstream-keepalive-connections": "100",  # 上游连接保持数
                    "upstream-keepalive-timeout": "60",       # 上游连接超时
                    "client-header-timeout": "60s",          # 客户端超时设置
                    "client-body-timeout": "60s",
                    "proxy-connect-timeout": "60s",
                    "proxy-read-timeout": "60s",
                    "proxy-send-timeout": "60s"
                },
                "service": {
                    "enabled": True,
                    "type": kwargs.get("service_type", "LoadBalancer"),
                    "externalTrafficPolicy": "Local"
                },
                "admissionWebhooks": {
                    "enabled": True,
                    "patch": {
                        "enabled": True,
                        "resources": {      # 降低 webhook 资源请求
                            "requests": {
                                "cpu": "50m",
                                "memory": "50Mi"
                            },
                            "limits": {
                                "cpu": "100m",
                                "memory": "100Mi"
                            }
                        }
                    }
                },
                "minReadySeconds": 0,          # 加快 Pod 就绪时间
                "terminationGracePeriodSeconds": 30,  # 优化终止时间
                "startupProbe": {              # 添加启动探针
                    "enabled": True,
                    "initialDelaySeconds": 5,
                    "periodSeconds": 5,
                    "timeoutSeconds": 2,
                    "failureThreshold": 3,
                    "httpGet": {
                        "path": "/healthz",
                        "port": 10254,
                        "scheme": "HTTP"
                    }
                },
                "readinessProbe": {            # 优化就绪探针
                    "enabled": True,
                    "initialDelaySeconds": 5,
                    "periodSeconds": 5,
                    "timeoutSeconds": 2,
                    "failureThreshold": 3,
                    "httpGet": {
                        "path": "/healthz",
                        "port": 10254,
                        "scheme": "HTTP"
                    }
                },
                "livenessProbe": {             # 优化存活探针
                    "enabled": True,
                    "initialDelaySeconds": 10,
                    "periodSeconds": 10,
                    "timeoutSeconds": 2,
                    "failureThreshold": 3,
                    "httpGet": {
                        "path": "/healthz",
                        "port": 10254,
                        "scheme": "HTTP"
                    }
                }
            },
            "defaultBackend": {
                "enabled": True,
                "replicaCount": 1,
                "resources": {
                    "requests": {
                        "cpu": "10m",
                        "memory": "20Mi"
                    },
                    "limits": {
                        "cpu": "20m",
                        "memory": "40Mi"
                    }
                },
                "minReadySeconds": 0,
                "startupProbe": {
                    "enabled": True,
                    "initialDelaySeconds": 5,
                    "periodSeconds": 5,
                    "timeoutSeconds": 2,
                    "failureThreshold": 3,
                    "httpGet": {
                        "path": "/healthz",
                        "port": 8080,
                        "scheme": "HTTP"
                    }
                }
            }
        }

        # TLS 配置
        if kwargs.get("default_tls", True):
            values["controller"]["extraArgs"] = {
                "default-ssl-certificate": f"{self.namespace_name}/tls-secret"
            }

        # 合并用户提供的额外配置
        if "values" in kwargs:
            values.update(kwargs["values"])

        # 创建带有更长超时时间的资源选项
        resource_opts = pulumi.ResourceOptions(
            custom_timeouts=pulumi.CustomTimeouts(
                create="10m",    # 增加创建超时时间到10分钟
                update="10m",
                delete="5m"
            )
        )

        release: helm.Release = helm.Release(
            self.name,
            helm.ReleaseArgs(
                chart="ingress-nginx",
                version=chart_version,
                namespace=self.namespace.metadata["name"],
                repository_opts=helm.RepositoryOptsArgs(
                    repo=repository
                ),
                values=values,
                timeout=600,  # 设置 Helm 超时为 600 秒（10分钟）
            ),
            opts=resource_opts
        )
        self._resource = release
        return release, self.namespace