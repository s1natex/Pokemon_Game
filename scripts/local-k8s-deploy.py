from subprocess import run
cmds = [
    ["kubectl","config","use-context","docker-desktop"],
    ["kubectl","apply","-f","k8s/app/namespace.yaml"],
    ["kubectl","apply","-f","k8s/app/configmap.yaml"],
    ["kubectl","apply","-f","k8s/app/secret.yaml"],
    ["kubectl","apply","-f","k8s/app/rbac.yaml"],
    ["kubectl","apply","-f","k8s/app/"]
]
for c in cmds:
    run(c, check=True)

# python scripts/local-k8s-deploy.py
# kubectl -n app get pods -w
