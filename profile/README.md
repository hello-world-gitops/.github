# Hello World: GitOps

This organization contains an end-to-end GitOps reference architecture for an **Everything-as-Code** fleet of Red Hat OpenShift clusters.
The repos in this org are meant to demonstrate how an organization can manage their code repositories to support a GitOps deployment pattern.
**This is not a one-solution-fits-all architecture.**
This is a reference architecture you can review and either fork the repos or reference pieces of the architecture as your create your own solution.

Hello World GitOps uses the following products:

* Red Hat OpenShift Container Platform
* Red Hat Advanced Cluster Management (ACM) for Kubernetes
* Red Hat OpenShift GitOps (Argo CD)

The reference architecture has 3 OpenShift clusters: Dev, Stage, and Hub.
Dev and Stage host development and staging applications respectively.
Hub hosts ACM and manages the Dev and Stage clusters.
Additionally, Hub should be used to host other shared applications (think artifact registry, container registry, secret server, etc.).

**NOTE:** To keep this project smaller, I elected to only feature a dev and stage environment.
Additional environments could be implemented following the same pattern that dev and stage use.

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

**All cluster and application configuration should be managed as code in Git repositories stored in a central Git server (GitHub, GitLab, etc.).**

OpenShift GitOps is deployed to all three clusters.
Applications are deployed to the clusters through the default cluster-wide Argo CD instance that OpenShift GitOps provides.
The Argo AppProject and Application configurations for all applications in a given cluster are stored in the *gitops-clustername* repo.
For example, the configuration to deploy all development applications is in the *gitops-dev* repo.

The GitOps repo for each cluster is deployed by ACM from the Hub cluster.

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
	end

	subgraph dev [Dev OpenShift Cluster]
	GitOpsDev["OpenShift GitOps<br />(Argo CD)"]
	DevApplications["Development Applications"]
	end

	Admin -. "Manually deploys 'bootstrap' repo<br />(This only happens once, everything<br />past this point is automated)" .-> ACM

	ACM -- "Continously deploys<br />'gitops-hub' repo" --> GitOpsHub
	GitOpsHub -- "Continously deploys<br />application repos" --> SharedApplications

	ACM -- "Continously deploys<br />'gitops-dev' repo" --> GitOpsDev
	GitOpsDev -- "Continously deploys<br />application repos" --> DevApplications

	ACM -- "Continously deploys<br />'gitops-stage' repo" --> GitOpsStage
	GitOpsStage -- "Continously deploys<br />application repos" --> StageApplications
```

## Layout

Each repository under the hello-world-gitops organization tackles a different piece of the GitOps puzzle.

- bootstrap
    - Bootstraps the Red Hat OpenShift multi-cluster fleet using Red Hat Advanced Cluster Management (ACM)
- gitops-dev
    - OpenShift GitOps (Argo CD) configurations to deploy applications on the Dev cluster
- gitops-stage
    - OpenShift GitOps (Argo CD) configurations to deploy applications on the Stage cluster
- gitops-hub
    - OpenShift GitOps (Argo CD) configurations to deploy applications on the Hub cluster

Still fleshing these repos out...
<s>
- policy
    - Red Hat Advanced Cluster Management (ACM) policies supporting the hello-world-gitops fleet
- app-1-helm
    - Code to deploy hello-world application
- app-1-code
    - Code to build the hello-world application container image
</s>

**NOTE: All repos in the hello-world-gitops org are subject to change.
Do not point your deployments to these repos.**
If you want to take any pieces of hello-world-gitops, fork the repos and deploy those to your clusters.

## Deploying

**I don't expect anyone to actually deploy this from GitHub.**
These repos exist to demonstrate how to configure an OpenShift fleet using the GitOps pattern.
I would recommend taking a look at the repos individually and adding pieces from them into your solution as needed.
If you're at square one and need a place to start, feel free clone the repos in this org and use the reference architecture as is.

To deploy, you will need 3 OpenShift clusters.
They can be Single-Node OpenShift (SNO) deployments if you're testing things out.

Install ACM on the Hub cluster and import the other two clusters.
Make sure the clusters are named dev and stage in ACM.
(The hub cluster in ACM will always be called *local-cluster*.)

- Log into the hub cluster with `oc`
- Clone the bootstrap repo
- Run `make install`

The bootstrap repo will create the necessary ACM applications, which will create Argo projects on the clusters, which will deploy applications.

## FAQ

### Will this architecture work for an organization that scales across multiple clusters per environment?

Redundant, geographically distributed environments could be implemented following a similar pattern to dev/stage.
For example, if an organization has an east and west cluster for their stage environment, the resources for stage in this reference architecture could be duplicated as *stage-east* and *stage-west*.

This architecture may not be feasible for a large number of clusters per environment due to the amount of configuration required.
For example, if an organization has 400 edge clusters for their stage environment, they would need to manage 400 GitOps (Argo configuration) repos.
