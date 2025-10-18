# DevSecOps: Pokemon Game Architecture
[![app-ci](https://github.com/s1natex/Pokemon_Game/actions/workflows/app-ci.yml/badge.svg)](https://github.com/s1natex/Pokemon_Game/actions/workflows/app-ci.yml)
- ### [Setup Instructions](./docs/setup.md)
- ### [Screenshots](./docs/screenshots.md)
## Project Overview:
- Dummy app only with critical functionalities
- `FRONTEND`: FastAPI exposed via AWS ALB Ingress
- `BACKEND`: Independent FastAPI microservices
  - Pokémon Manager
  - Trainer Manager
  - Battle Manager
  - Scheduler
  - Pokémon Fetcher
- `DATA FLOW`: RESTful APIs and internal event-based communication through asynchronous job scheduling
- `INFRASTRUCTURE`: Managed via Terraform with isolated modules:
  - **terraform/bootstrap**: S3 state bucket and DynamoDB lock table
  - **terraform/eks**: EKS cluster, Fargate profiles, networking
  - **terraform/observability**: CloudWatch, X-Ray, and FluentBit logging
- `CI/CD`:
  - `app-ci`: runs on code changes under `./app/`
    - Unit & runtime tests via pytest
    - Security scans with Bandit (SAST)
    - Dynamic image tagging - `SERVICE_NAME-DDMMYYYY-HHMM-SHA`
    - Auto-updates Kubernetes manifests with new image tags
  - `DEPLOYMENT`: ArgoCD manages application lifecycle, syncing manifests from GitHub to Kubernetes
- `Observability`:
  - CloudWatch logs and metrics enabled via namespace labeling
  - Centralized metrics dashboard via Prometheus-compatible exporters
  - Automated patching script ensures logging and metrics connectivity
- `SECURITY & COMPLIANCE`:
    - Principle of Least Privilege enforced via IAM roles
    - Secure state management (S3 with encryption + DynamoDB locks)
    - Bandit SAST integrated into CI for code vulnerability detection
    - ALB ingress with controlled namespace-level access for `Frontend` and `ArgoCD`
- `PERFORMANCE & SCALABILITY`: The system is architected to handle up to 50,000 concurrent users
    - EKS-managed horizontal scaling per deployment
    - Load balancing via AWS ALB
    - Fargate auto-provisioning for stateless workloads
    - Minimal inter-service coupling allowing independent scaling
    - Terraform modules enable easy environment replication
## Design Choices Overview:

## Project Diagram:
