# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import pulumi
import pulumi_kubernetes.helm.v3 as helm
import pulumi_kubernetes.core.v1 as core

def deploy():
    ns = core.Namespace(
        "cert-manager",
        metadata={"name": "cert-manager"},
        opts=pulumi.ResourceOptions(additional_secret_outputs=["metadata.name"]),
    )

    release = helm.Release(
        "cert-manager",
        helm.ReleaseArgs(
            chart="cert-manager",
            version="v1.14.4",
            namespace=ns.metadata["name"],
            create_namespace=True,
            repository_opts=helm.RepositoryOptsArgs(
                repo="https://charts.jetstack.io"
            ),
            values={"installCRDs": True},
        )
    )

    return release, ns
