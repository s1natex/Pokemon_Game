from subprocess import run
cmds = [
    ["kubectl","config","use-context","docker-desktop"],
    ["helm","repo","add","ingress-nginx","https://kubernetes.github.io/ingress-nginx"],
    ["helm","repo","update"],
    ["helm","upgrade","--install","ingress-nginx","ingress-nginx/ingress-nginx","-n","ingress-nginx","--create-namespace"],
    ["kubectl","-n","ingress-nginx","rollout","status","deploy/ingress-nginx-controller","--timeout=180s"],
    ["kubectl","apply","-f","k8s/app/namespace.yaml"],
    ["kubectl","apply","-f","k8s/app/configmap.yaml"],
    ["kubectl","apply","-f","k8s/app/secret.yaml"],
    ["kubectl","apply","-f","k8s/app/rbac.yaml"],
    ["kubectl","apply","-f","k8s/app/pokemon-manager.yaml"],
    ["kubectl","apply","-f","k8s/app/trainer-manager.yaml"],
    ["kubectl","apply","-f","k8s/app/battle-manager.yaml"],
    ["kubectl","apply","-f","k8s/app/scheduler.yaml"],
    ["kubectl","apply","-f","k8s/app/pokemon-fetcher.yaml"],
    ["kubectl","apply","-f","k8s/app/frontend.yaml"]
]
for c in cmds:
    run(c, check=True)

# python scripts/local-k8s-deploy.py
# kubectl -n app get pods -w
