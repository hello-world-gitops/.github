from rhdiagrams import Diagram

from diagrams.onprem.vcs import Git
from diagrams.onprem.gitops import ArgoCD

from rhdiagrams.redhat.software import KubernetesPodBlack
from rhdiagrams.redhat.software import ContainerImageBlack
from rhdiagrams.redhat.products import Openshift

description = """
Hello World: GitOps. The 'bootstrap' repo is deployed manually to the Hub
cluster. Bootstrap creates ACM applications (subscriptions) to automatically
deploy the 'policy', 'gitops-hub', 'gitops-dev' and 'gitops-stage' repos
against the fleet. The configurations deployed by the 'gitops' repos create
Argo CD applications to automatically deploy applications to the fleet.
"""

with Diagram(description, "./hello-world-gitops", direction="TB"):
    bootstrap = Git("'bootstrap' Repo")
    policy = Git("'policy' Repo")
    gitops_hub = Git("'gitops_hub' Repo")
    gitops_dev = Git("'gitops_dev' Repo")
    gitops_stage = Git("'gitops_stage' Repo")

    acm = Openshift("ACM")

    hub = Openshift("Hub Cluster")
    dev = Openshift("Dev Cluster")
    stage = Openshift("Stage Cluster")

    hub_argo = ArgoCD("Hub GitOps\n(Argo CD)")
    dev_argo = ArgoCD("Dev GitOps\n(Argo CD)")
    stage_argo = ArgoCD("Stage GitOps\n(Argo CD)")

    bootstrap >> acm
    acm >> policy
    acm >> gitops_hub
    acm >> gitops_dev
    acm >> gitops_stage

    gitops_hub >> hub
    gitops_dev >> dev
    gitops_stage >> stage

    policy >> hub
    policy >> dev
    policy >> stage
