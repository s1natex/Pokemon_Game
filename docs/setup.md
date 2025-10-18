- #### Infrastructure is managed from local pc and app via GitHub Actions CI and in cluster ArgoCD operator
- #### Prerequisites
    - `Python3`
    - `Terraform`
    - `Kubectl`
    - `Git`
    - `Git Bash CLI`
    - `AWS-CLI`
    - AWS local pc credentials set as environment variables
    - `Docker Desktop`(for local testing)
    - `Pytest`(running tests locally)
    - `git clone https://github.com/s1natex/Pokemon_Game`
# Initial Setup
- #### Initial Bootstrap for `S3 Remote state` and `OIDC`
```
# Bootstrap build is managed from local state file and the rest stored in remote s3
cd ./terraform/bootstrap
terraform init
terraform plan
terraform Apply
```
- #### Launch the `EKS` Cluster
```
cd ./terraform/eks
```
- Create terraform/eks/terraform.tfvars
```
region             = "eu-central-1"
project            = "pokemon-game"
state_bucket       = "<use terraform output from bootstrap for bucket name>"
lock_table         = "pokemon-game-tf-locks"
cluster_name       = "pokemon-game-eks"
```
- Run terraform init with new buckets name
```
terraform init -reconfigure \
-backend-config="bucket=<use terraform output from bootstrap for bucket name>" \
-backend-config="key=eks/terraform.tfstate" \
-backend-config="region=eu-central-1" \
-backend-config="dynamodb_table=pokemon-game-tf-locks"
```
- Run Plan to validate correct infrastructure and apply
```
terraform plan
terraform apply

# Cluster Deploy may take about 10-15 minutes to fully deploy
```
- Verify Cluster is up
```
aws eks update-kubeconfig \
  --name pokemon-game-eks \
  --region eu-central-1 \
  --alias pokemon-game-eks
kubectl config use-context pokemon-game-eks
kubectl get nodes
kubectl -n kube-system get deploy aws-load-balancer-controller
kubectl -n app get pods,svc,ingress
```
- #### Deploy the actual Cluster using a `Python` script from project root
```
python3 ./scripts/eks-k8s-deploy.py
```
- #### Deploy `Monitoring and Logging`
```
cd ./terraform/observability/
```
- Run init with new bucket name
```
terraform init -reconfigure \
-backend-config="bucket=<use terraform output from bootstrap for bucket name>" \
-backend-config="key=observability/terraform.tfstate" \
-backend-config="region=eu-central-1" \
-backend-config="dynamodb_table=pokemon-game-tf-locks"
```
- Create terraform/observability/terraform.tfvars
```
region             = "eu-central-1"
project            = "pokemon-game"
state_bucket       = "<use terraform output from bootstrap for bucket name>"
lock_table         = "pokemon-game-tf-locks"
cluster_name       = "pokemon-game-eks"
alb_arn_suffix = "use the command below for value"
```
- `alb_arn_suffix` value command
```
export MSYS_NO_PATHCONV=1
export MSYS2_ARG_CONV_EXCL="*"
REGION="eu-central-1"

aws elbv2 describe-load-balancers --region "$REGION" \
  --query 'LoadBalancers[?Type==`application`].LoadBalancerArn' --output text \
| sed -E 's|^arn:aws:elasticloadbalancing:[^:]+:[0-9]+:loadbalancer/||'
```
- Run Plan to validate correct infrastructure and apply
```
terraform plan
terraform apply
```
- Patch Cloudwatch and Cloudwatch Logs from project root
```
python3 ./scripts/cloudwatch-patch.py
```
# Validation Checklist
- #### Grab `Frontend` address and access via browser
```
kubectl -n app get ingress app-alb
```
- #### Access `Cloudwatch` and `Cloudwatch Logs`
```
# Logs appear under CloudWatch Logs → /eks/pokemon-game/app
# Dashboard: CloudWatch → Dashboards → pokemon-game-observability
```
- #### Run `Stress test` to stimulate traffic to the cluster from project root
```
# Script asks for frontend address
python3 ./scripts/populate_dashboard.py
```
- #### Access and Login to `ArgoCD` UI
```
# Address
kubectl -n argocd get ingress argocd-alb -o jsonpath='{.status.loadBalancer.ingress[0].hostname}{"\n"}'

# Username: admin

# Password:
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
```
- #### `CI/CD` Testing
    - If using fork Update `DOCKERHUB_TOKEN` and `DOCKERHUB_USERNAME` in Repository actions -> secrets
    - Make some changes to `./app/` dir
    - `Commit` and `push` to GitHub Repository
    - CI will pick up run `unit` and `runtime` tests via `compose`, `sast` scan, `build`, `tag`(name-date-time-sha), `push` to DockerHub and `commit back` to Repository with `[skip-ci]` flag
    - `ArgoCD` will detect changes (default autosync every 3 minutes) and deploy the new images to the cluster
    - In this Project `Rollbacks` are possible manually via `deactivating autosync` and the native `ArgoCD rollback feature` with using `Git` commands
# Clean Up
- Destroy Monitoring build
```
cd ./terraform/observability/
terraform destroy
```
- Cleanup EKS Deployment (optional for experiments) from project root
```
python3 ./scripts/eks-k8s-destroy.py
```
- Destroy Terraform EKS build
```
cd ./terraform/eks
terraform destroy
```
- Empty S3 Bucket on AWS UI
- Destroy Bootstrap build
```
cd ./terraform/bootstrap
terraform destroy
```
- CLI Context switch
```
kubectl config use-context docker-desktop
kubectl config current-context
```
