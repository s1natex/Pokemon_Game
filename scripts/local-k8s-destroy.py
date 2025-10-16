from subprocess import run
cmds = [
    ["kubectl","config","use-context","docker-desktop"],
    ["kubectl","delete","-f","k8s/app/frontend.yaml","--ignore-not-found=true"],
    ["kubectl","delete","-f","k8s/app/","--ignore-not-found=true"],
    ["kubectl","delete","namespace","app","--ignore-not-found=true"],
    ["helm","uninstall","ingress-nginx","-n","ingress-nginx"],
    ["kubectl","delete","namespace","ingress-nginx","--ignore-not-found=true"]
]
for c in cmds:
    run(c, check=True)

# python scripts/local-k8s-destroy.py
# kubectl get ns app
