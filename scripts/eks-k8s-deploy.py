from subprocess import run, PIPE, CalledProcessError

apply_cmds = [
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
    ["kubectl","apply","-f","k8s/app/ingress-alb.yaml"],
    ["kubectl","-n","app","delete","ingress","app-ingress","--ignore-not-found=true"],
    ["kubectl","apply","-f","k8s/argocd/"]
]

for c in apply_cmds:
    run(c, check=True)

print("=== validation ===")

validate_cmds = [
    ["kubectl","-n","app","get","pods"],
    ["kubectl","-n","app","get","svc"],
    ["kubectl","-n","app","get","ingress"],
    ["kubectl","-n","argocd","get","pods"],
    ["kubectl","-n","argocd","get","svc","argocd-server"],
    ["kubectl","-n","argocd","get","ingress","argocd-alb","-o","jsonpath={.status.loadBalancer.ingress[0].hostname}"]
]

for c in validate_cmds:
    try:
        out = run(c, check=True, stdout=PIPE)
        if out.stdout:
            print(out.stdout.decode(errors="ignore"))
    except CalledProcessError:
        pass
