from subprocess import run
cmds = [
    ["kubectl","config","use-context","docker-desktop"],
    ["kubectl","delete","-f","k8s/app/"],
    ["kubectl","delete","namespace","app"],
    ["helm","uninstall","ingress-nginx","-n","ingress-nginx"],
    ["kubectl","delete","namespace","ingress-nginx"]
]
for c in cmds:
    run(c, check=True)

# python scripts/local-k8s-destroy.py
# kubectl get ns app
