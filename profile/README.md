# OpenShift Multi-Cluster GitOps

This organization contains an end-to-end, **Everything-as-Code** reference architecture for multi-cluster management of Red Hat OpenShift.
The repos in this org are meant to demonstrate how an organization can manage their code repositories to support a GitOps deployment pattern for cluster configurations and applications.

**This is not a one-solution-fits-all architecture.** This is a reference architecture you can review and either fork the repos or reference pieces of the architecture as your create your own solution.

**The reference architecture does not include deployment of OpenShift onto any platform.** Everything in this organization for day 2, post-install configuration and management of all OpenShift clusters.

## Before Jumping In

**If you are starting from scratch, I recommend using [Hybrid Cloud Patterns] instead of this reference architecture for a couple reasons:**

* [Multicloud GitOps] is a validated pattern that can configure a fleet of clusters with significantly less work than this reference architecture.
* Hybrid Cloud Patterns are constantly updated by Red Hat Engineers supporting the project.
* This reference architecture will not be updated.

If you have existing multicluster set up and are looking for examples of other architectures, read on!

## Architecture Breakdown

The reference architecture uses the following products:

* [Red Hat OpenShift Container Platform]
* [Red Hat Advanced Cluster Management (ACM) for Kubernetes]
* [Red Hat OpenShift GitOps (Argo CD)]

The reference architecture has 3 OpenShift clusters: Dev, Stage, and Hub.
Dev and Stage host development and staging applications respectively.
Hub hosts ACM and manages the Dev and Stage clusters.
Additionally, Hub should be used to host other shared applications (artifact registry, container registry, secret server, etc.).

```mermaid
graph TD
        Dev["<b>Dev OpenShift Cluster</b><br />(OpenShift GitOps,<br />Development Applications)"]
        Hub["<b>Hub OpenShift Cluster</b><br />(Red Hat Advanced Cluster Management (ACM) for Kubernetes,<br />OpenShift GitOps, Shared Applications)"]
        Stage["<b>Stage OpenShift Cluster</b><br />(OpenShift GitOps,<br />Staging Applications)"]

        Git["<b>Git Server</b><br />(GitHub, GitLab, etc.)"]

        Dev -. "Continuously<br />pulls code" .- Git
        Hub -. "Continuously<br />pulls code" .- Git
        Stage -. "Continuously<br />pulls code" .- Git

        Hub -- Managed by ACM --> Dev
        Hub -- Managed by ACM --> Stage
```

**NOTE:** To keep this project smaller, I elected to only feature a dev and stage environment.
Additional environments can be implemented following the same pattern that dev and stage use.

**All cluster and application configuration is managed as code in Git repositories stored in a central Git server (GitHub, GitLab, etc.).**

[Helm] is used extensively throughout the Git repos in this organization.
Helm charts allow for YAML manifests to be templated and looped over.
This enables cluster administrators to easily make changes through variables in the *Values.yaml* file in each repo instead of directly as YAML in Kubernetes manifests.

The Helm charts in each Git repo are deployed through OpenShift GitOps (Argo CD).
OpenShift GitOps is deployed to all three clusters through an ACM governance policy.
OpenShift GitOps creates a cluster-wide Argo CD instance in the `openshift-gitops` namespace which is used to deploy applications to the cluster.

Argo CD is configured through Kubernetes manifests.
It provides two *Custom Resources* to configure applications for continuous deployment.

An Argo CD *AppProject* is a group of applications that Argo CD manages.
It includes the metadata about the group of applications.
This reference architecture expects that an Argo CD AppProject match 1:1 with an OpenShift Namespace (Project).
Any applications deployed into the same namespace should be included in the same AppProject.

An Argo CD *Application* contains configurations for a single application that Argo CD manages.
It includes the Git repo URL, Git branch to deploy, OpenShift namespace to deploy into, etc.
The Git repo for the application being deployed can contain straight YAML manifests, Kustomize, or Helm charts.
(The example applications in this organization are Helm Charts.)

The Argo CD AppProject and Application configurations for all applications in a given cluster are stored in the *gitops-clustername* repo.
For example, the configuration to deploy all development applications is in the [gitops-dev] repo.
*theme-park-api-dev* is an AppProject and OpenShift Namespace that will be deployed from that repo.
There are three Applications that will be deployed to the AppProject/Namespace: *hershey-park-dev*, *kings-dominion-dev*, and *six-flags-dev.*
Each of the above applications is deployed from Helm charts in [this repo][theme-park-api-chart].

The GitOps repo for each cluster is continuously deployed through an ACM Subscription (Application) on the Hub cluster.
The ACM subscription is created through a one-time bootstrapping process that kicks off GitOps configuration and management across the clusters.

```mermaid
graph TD
	Admin["Admin 🧑‍💻"]
	ACM["Red Hat Advanced Cluster<br />Mangement (ACM) for Kubernetes"]

	subgraph stage [Stage OpenShift Cluster]
	GitOpsStage["OpenShift GitOps<br />(Argo CD)"]
	StageApplications["Staging Applications"]
	end

	subgraph hub [Hub Openshift Cluster]
	ACM
	GitOpsHub["OpenShift GitOps<br />(Argo CD)"]
	SharedApplications["Shared Applications"]
	ACMPolicies["ACM Policies"]
	end

	subgraph dev [Dev OpenShift Cluster]
	GitOpsDev["OpenShift GitOps<br />(Argo CD)"]
	DevApplications["Development Applications"]
	end

	Admin -. "Manually deploys 'bootstrap' repo<br />(This only happens once, everything<br />past this point is automated)" .-> ACM

	ACM -- "Continously deploys<br />'gitops-hub' repo" --> GitOpsHub
	GitOpsHub -- "Continously deploys<br />application repos" --> SharedApplications
	GitOpsHub -- "Continously deploys<br />'policy' repo" --> ACMPolicies

	ACM -- "Continously deploys<br />'gitops-dev' repo" --> GitOpsDev
	GitOpsDev -- "Continously deploys<br />application repos" --> DevApplications

	ACM -- "Continously deploys<br />'gitops-stage' repo" --> GitOpsStage
	GitOpsStage -- "Continously deploys<br />application repos" --> StageApplications
```

## Git Repositories

All repositories under this organization support the reference architecture.

**NOTE: All repos under this organization are subject to change.
Do not point your deployments to these repos!**
If you want to use any code in these repos, fork the repos and deploy those to your clusters.

### Bootstrap

- [bootstrap]
    - Bootstrap multi-cluster management of Red Hat OpenShift through Red Hat Advanced Cluster Management (ACM) for Kubernetes

### Per-Cluster GitOps (Argo CD) Configurations

- [gitops-dev]
    - OpenShift GitOps (Argo CD) configurations to deploy applications on the Dev cluster
- [gitops-hub]
    - OpenShift GitOps (Argo CD) configurations to deploy applications on the Hub cluster
- [gitops-stage]
    - OpenShift GitOps (Argo CD) configurations to deploy applications on the Stage cluster

### ACM Governance Policy

- [policy]
    - Red Hat Advanced Cluster Management (ACM) for Kubernetes governance policies for all clusters

### Example Application

- [theme-park-api-chart]
    - Helm chart to deploy an example REST API. This is deployed to the dev and stage environments through OpenShift GitOps (Argo CD).

## Deploying

**I don't expect anyone to actually deploy this from GitHub.**

These repos exist to demonstrate how to configure multi-cluster management of OpenShift clusters using the GitOps pattern.
I would recommend taking a look at the repos individually and adding pieces from them into your solution as needed.
If you're at square one and need a place to start, feel free clone the repos in this org and use the reference architecture as is.

To deploy, you will need 3 OpenShift clusters.
I use Single-Node OpenShift (SNO) deployments to test things out.

Install ACM on the Hub cluster and import the other two clusters (or create the clusters from ACM, your call 🤷.
Make sure the clusters are named `dev` and `stage` in ACM.
(The hub cluster in ACM will always be called `local-cluster`.)

- Log into the hub cluster with `oc`
- Clone the bootstrap repo
- Run `make install`

The bootstrap repo will create the necessary ACM subscriptions, which will create Argo projects on the clusters, which will deploy applications!

## FAQ

### Will this architecture work for an organization that scales across multiple clusters per environment?

Redundant, geographically distributed environments could be implemented following a similar pattern to dev/stage.
For example, if an organization has an east and west cluster for their stage environment, the resources for stage in this reference architecture could be duplicated as *stage-east* and *stage-west*.

This architecture may not be feasible for a large number of clusters per environment due to the amount of configuration required.
For example, if an organization has 400 edge clusters for their stage environment, they would need to manage 400 GitOps (Argo configuration) repos.

[AppProject Example]: https://github.com/hello-openshift-multicluster-gitops/gitops-dev/blob/main/values.yaml
[Helm]: https://helm.sh/
[Hybrid Cloud Patterns]: https://hybrid-cloud-patterns.io
[Multicloud GitOps]: https://hybrid-cloud-patterns.io/patterns/multicloud-gitops
[Red Hat Advanced Cluster Management (ACM) for Kubernetes]: https://www.redhat.com/en/technologies/management/advanced-cluster-management
[Red Hat OpenShift Container Platform]: https://docs.openshift.com/container-platform/latest
[Red Hat OpenShift GitOps (Argo CD)]: https://docs.openshift.com/container-platform/latest/cicd/gitops/gitops-release-notes.html
[bootstrap]: https://github.com/hello-openshift-multicluster-gitops/bootstrap
[gitops-dev]: https://github.com/hello-openshift-multicluster-gitops/gitops-dev
[gitops-hub]: https://github.com/hello-openshift-multicluster-gitops/gitops-hub
[gitops-stage]: https://github.com/hello-openshift-multicluster-gitops/gitops-stage
[policy]: https://github.com/hello-openshift-multicluster-gitops/policy
[theme-park-api-chart]: https://github.com/hello-openshift-multicluster-gitops/theme-park-api-chart
