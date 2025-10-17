from subprocess import run

cmds = [
    ["aws","eks","update-kubeconfig","--name","pokemon-game-eks","--region","eu-central-1","--alias","pokemon-game-eks"],
    ["kubectl","config","use-context","pokemon-game-eks"],
    ["kubectl","delete","-f","k8s/app/ingress-alb.yaml","--ignore-not-found=true"],
    ["kubectl","delete","-f","k8s/app/","--ignore-not-found=true"],
    ["kubectl","delete","namespace","app","--ignore-not-found=true"],
    ["echo", "==================================="],
    ["echo", "Deployment destroyed successfully"],
    ["echo", "==================================="],
    ["kubectl", "get", "ns", "|", "grep", "app"],
    ["kubectl", "get", "pods", "-A"]
]

for c in cmds:
    run(c, check=True)
