# qubit-note: Terraform | Introduction to Terraform


## Overview

In this series of qubit notes we will be looking into Terrafor.
Terraform is an Infrastructure as Code (IaC) tool created by HashiCorp. 
It lets you define and manage infrastructure (servers, databases, networks, cloud resources, Kubernetes clusters, etc.) using configuration files instead of manually clicking through web consoles.

## Introduction to Terraform

Let's start by trying to understand what problems Terraform helps us to solve.

### What problem does Terraform solve?

Without Terraform, infrastructure is often created manually:

1. Someone logs into AWS, Azure, or GCP.
2. They click through menus to create VMs, databases, networks, and security groups.
3. Another person repeats the process in another environment.
4. Eventually, nobody remembers exactly how everything was configured.

This however creates several problems:

* Inconsistent environments: Development, staging, and production drift apart.
* Human error: Manual configuration mistakes are common.
* Poor documentation: Infrastructure exists, but its configuration lives only in people's heads.
* Difficult scaling: Creating dozens or hundreds of resources manually is slow.
* No version history: You can't easily see who changed infrastructure or roll back changes.

Terraform addresses these issues by treating infrastructure like software.


### How Terraform works

Instead of manually creating resources, you write a configuration file.

Example:

```hcl
resource "aws_instance" "web" {
  ami           = "ami-123456789"
  instance_type = "t3.micro"
}
```

Terraform then:

1. Reads your configuration.
2. Compares it to the current infrastructure.
3. Determines what needs to change.
4. Applies only those changes.


Thus, with Terraform, your infrastructure lives in code files that can be:

* stored in Git
* reviewed in pull requests
* version controlled
* reused

Example project:

```
terraform/
    main.tf
    variables.tf
    outputs.tf
```

The HCL language follows a declarative approach that is you describe the desired end state:

> "I want three EC2 instances."

Not:

> "Create instance A, then B, then C."

Terraform figures out how to reach that state.



#### Planning before changes

One of Terraform's best features is:

```bash
terraform plan
```

It shows exactly what will happen before making changes.

Example:

```
+ Create EC2 Instance
~ Modify Security Group
- Destroy Old Database
```

This reduces surprises.


#### State management

Terraform keeps track of what it manages in a state file (`terraform.tfstate`). The state records things like:

* resource IDs
* IP addresses
* dependencies
* current configuration

This lets Terraform know:

* what already exists
* what needs updating
* what should be deleted


#### Multi-cloud support

Terraform works with many providers through plugins.
Examples include:

* AWS
* Azure
* Google Cloud
* Kubernetes
* VMware
* GitHub
* Cloudflare
* Datadog
* Docker

You can even manage multiple providers in the same project.
Example:

* AWS infrastructure
* Kubernetes cluster
* Cloudflare DNS

all from one configuration.



#### Reusable modules

Instead of copying configuration repeatedly, you can create modules.
For example:

```
modules/
    web-server/
    database/
    networking/
```

Then reuse them across projects.
his is similar to calling functions in programming.



#### Collaboration

Terraform integrates well with Git workflows.
Typical workflow:

```
Developer
     ↓
Edit Terraform code
     ↓
Commit to Git
     ↓
Pull Request
     ↓
Review
     ↓
terraform plan
     ↓
Approve
     ↓
terraform apply
```

This makes infrastructure changes auditable and repeatable.



### Example use cases

Terraform can provision:

* Virtual machines
* Kubernetes clusters
* VPCs and networks
* Load balancers
* DNS records
* Databases
* Storage buckets
* IAM users and roles
* Monitoring resources

For example, a single Terraform project might create:

* A VPC
* Public and private subnets
* Security groups
* An RDS database
* EC2 web servers
* An Application Load Balancer
* Route 53 DNS records

with one command.


### Advantages

* **Consistency:** Every environment is built the same way.
* **Automation:** Eliminates repetitive manual setup.
* **Version control:** Infrastructure changes are tracked in Git.
* **Repeatability:** Easily recreate environments.
* **Scalability:** Manage hundreds or thousands of resources.
* **Provider agnostic:** Works across multiple cloud platforms.
* **Preview changes:** `terraform plan` shows intended changes before applying them.



### Limitations

* **State management:** The state file must be stored securely and shared carefully in team environments.
* **Learning curve:** Understanding HCL (HashiCorp Configuration Language), modules, providers, and state takes time.
* **Not a configuration management tool:** Terraform creates infrastructure but doesn't configure software inside servers. Tools like Ansible, Chef, or cloud-init are often used alongside it.
* **Drift:** If someone manually changes resources outside Terraform, the actual infrastructure can diverge from the code, although Terraform can detect many such differences during planning.



Terraform addresses several common problems related to infrastructure management. Here is a structured overview:

Manual Configuration Complexity:

Problem: Manually provisioning and configuring infrastructure is error-prone, time-consuming, and inconsistent.
Solution: Terraform uses code to define infrastructure, ensuring repeatability and reducing manual errors through Infrastructure as Code (IaC).
Lack of Version Control:

Problem: Managing infrastructure changes manually makes tracking modifications difficult.
Solution: Terraform configurations can be version-controlled, allowing teams to track changes, revert to previous states, and collaborate effectively.
Inconsistent Environments:

Problem: Deploying similar environments (development, staging, production) manually can lead to inconsistencies.
Solution: Terraform enables reproducible and deterministic environment provisioning across different stages.
Configuration Drift:

Problem: Over time, infrastructure can drift from the desired state due to manual changes, leading to configuration discrepancies.
Solution: Terraform’s plan feature detects drift and allows automatic or manual synchronization to desired state.
Multi-Cloud and Provider Management:

Problem: Managing multiple cloud providers or services manually increases complexity.
Solution: Terraform supports multiple providers and integrates with various services, allowing a unified tool for diverse environments.
Change Management and Automation:

Problem: Manual updates are risky and hard to coordinate.
Solution: Terraform automates updates via planned, incremental changes with clear previews (terraform plan) before applying (terraform apply).