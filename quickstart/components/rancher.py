# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import pulumi
import pulumi_kubernetes.helm.v3 as helm
import pulumi_kubernetes.core.v1 as core

def deploy(depends_on_release):
    ns = core.Namespace("cattle-system", metadata={"name": "cattle-system"})

    release = helm.Release(
        "rancher",
        helm.ReleaseArgs(
            chart="rancher",
            version="2.11.2",
            namespace=ns.metadata["name"],
            repository_opts=helm.RepositoryOptsArgs(
                repo="https://releases.rancher.com/server-charts/stable"
            ),
            values={
                "replicas": 1,
                "hostname": "rancher.local",
                "ingress": {"enabled": False},
                "service": {
                    "type": "NodePort",
                    "nodePort": 31000
                },
                "bootstrapPassword": "admin123"
            },
        ),
        opts=pulumi.ResourceOptions(depends_on=[depends_on_release])
    )

    return release
