from subprocess import run
cmds = [
    ["kubectl","config","use-context","docker-desktop"],
    ["helm","repo","add","ingress-nginx","https://kubernetes.github.io/ingress-nginx"],
    ["helm","repo","update"],
    ["helm","upgrade","--install","ingress-nginx","ingress-nginx/ingress-nginx","--namespace","ingress-nginx","--create-namespace"],
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
