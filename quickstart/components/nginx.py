# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import pulumi
from pulumi_kubernetes.apps.v1 import Deployment
from pulumi_kubernetes.core.v1 import Namespace

def deploy():
    app_labels = {"app": "nginx"}

    ns = Namespace(
        "nginx",
        metadata={"name": "nginx"},
        opts=pulumi.ResourceOptions(additional_secret_outputs=["metadata.name"]),
    )

    deployment = Deployment(
        "nginx",
        metadata={"namespace": ns.metadata["name"]},
        spec={
            "selector": {"match_labels": app_labels},
            "replicas": 1,
            "template": {
                "metadata": {"labels": app_labels},
                "spec": {
                    "containers": [{
                        "name": "nginx",
                        "image": "nginx:latest",
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

    return deployment, ns
