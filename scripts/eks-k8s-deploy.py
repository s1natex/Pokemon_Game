from subprocess import run
cmds = [
    ["aws","eks","update-kubeconfig","--name","pokemon-game-eks","--region","eu-central-1","--alias","pokemon-game-eks"],
    ["kubectl","config","use-context","pokemon-game-eks"],
    ["kubectl","apply","-f","k8s/app/namespace.yaml"],
    ["kubectl","apply","-f","k8s/app/configmap.yaml"],
    ["kubectl","apply","-f","k8s/app/secret.yaml"],
    ["kubectl","apply","-f","k8s/app/rbac.yaml"],
    ["kubectl","apply","-f","k8s/app/pokemon-manager.yaml"],
    ["kubectl","apply","-f","k8s/app/trainer-manager.yaml"],
    ["kubectl","apply","-f","k8s/app/battle-manager.yaml"],
    ["kubectl","apply","-f","k8s/app/scheduler.yaml"],
    ["kubectl","apply","-f","k8s/app/pokemon-fetcher.yaml"],
    ["kubectl","apply","-f","k8s/app/frontend.yaml"],
    ["kubectl","apply","-f","k8s/app/ingress-alb.yaml"]
]
for c in cmds:
    run(c, check=True)
