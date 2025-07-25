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
                "kind": "DaemonSet",  # 使用 DaemonSet 部署
                "hostNetwork": True,   # 使用主机网络
                "dnsPolicy": "ClusterFirstWithHostNet",  # 配置 DNS 策略
                "nodeSelector": {
                    "kubernetes.io/os": "linux"  # 只在 Linux 节点上运行
                },
                "tolerations": [
                    {
                        "key": "node-role.kubernetes.io/master",
                        "operator": "Exists",
                        "effect": "NoSchedule"
                    },
                    {
                        "key": "node-role.kubernetes.io/control-plane",
                        "operator": "Exists",
                        "effect": "NoSchedule"
                    }
                ],
                "resources": {
                    "requests": {
                        "cpu": "50m",
                        "memory": "90Mi"
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
                    "allowPrivilegeEscalation": True,
                    "capabilities": {
                        "drop": ["ALL"],
                        "add": ["NET_BIND_SERVICE"]
                    }
                },
                "config": {
                    "enable-real-ip": "true",
                    "use-forwarded-headers": "true",
                    "compute-full-forwarded-for": "true",
                    "use-proxy-protocol": "false",
                    "proxy-body-size": "50m",
                    "keep-alive": "75",
                    "keep-alive-requests": "100",
                    "upstream-keepalive-connections": "100",
                    "upstream-keepalive-timeout": "60",
                    "client-header-timeout": "60s",
                    "client-body-timeout": "60s",
                    "proxy-connect-timeout": "60s",
                    "proxy-read-timeout": "60s",
                    "proxy-send-timeout": "60s"
                },
                "service": {
                    "enabled": True,
                    "type": "NodePort",  # 使用 NodePort 服务类型
                    "externalTrafficPolicy": "Local"
                },
                "hostPort": {
                    "enabled": True,     # 启用 hostPort
                    "ports": {
                        "http": 80,
                        "https": 443
                    }
                },
                "admissionWebhooks": {
                    "enabled": True,
                    "patch": {
                        "enabled": True,
                        "resources": {
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
                "minReadySeconds": 0,
                "updateStrategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {
                        "maxUnavailable": 1
                    }
                },
                "terminationGracePeriodSeconds": 30,
                "startupProbe": {
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
                "readinessProbe": {
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
                "livenessProbe": {
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