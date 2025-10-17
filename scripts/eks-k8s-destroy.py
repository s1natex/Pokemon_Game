from subprocess import run, PIPE, CalledProcessError

destroy_cmds = [
    ["aws","eks","update-kubeconfig","--name","pokemon-game-eks","--region","eu-central-1","--alias","pokemon-game-eks"],
    ["kubectl","config","use-context","pokemon-game-eks"],
    ["kubectl","delete","-f","k8s/argocd/","--ignore-not-found=true"],
    ["kubectl","delete","-f","k8s/app/ingress-alb.yaml","--ignore-not-found=true"],
    ["kubectl","delete","-f","k8s/app/","--ignore-not-found=true"],
    ["kubectl","delete","namespace","app","--ignore-not-found=true"]
]

for c in destroy_cmds:
    run(c, check=True)

print("=== validation ===")

validate_cmds = [
    ["kubectl","get","ns"],
    ["kubectl","get","pods","-A"]
]

for c in validate_cmds:
    try:
        out = run(c, check=True, stdout=PIPE)
        if out.stdout:
            print(out.stdout.decode(errors="ignore"))
    except CalledProcessError:
        pass
