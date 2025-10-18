from subprocess import run

cmds = [
    ["kubectl", "label", "namespace", "app", "aws-observability=enabled", "--overwrite"],
    ["kubectl", "-n", "aws-observability", "get", "cm", "aws-logging"],
    ["aws", "eks", "describe-fargate-profile",
        "--cluster-name", "pokemon-game-eks",
        "--fargate-profile-name", "app",
        "--region", "eu-central-1",
        "--query", "fargateProfile.podExecutionRoleArn",
        "--output", "text"],
    ["aws", "iam", "list-attached-role-policies",
        "--role-name", "pokemon-game-eks-fargate-pod-exec"],
    ["kubectl", "-n", "app", "rollout", "restart", "deploy/frontend"],
    ["kubectl", "-n", "app", "rollout", "restart", "deploy/pokemon-manager"],
    ["kubectl", "-n", "app", "rollout", "restart", "deploy/trainer-manager"],
    ["kubectl", "-n", "app", "rollout", "restart", "deploy/battle-manager"],
    ["kubectl", "-n", "app", "rollout", "restart", "deploy/scheduler"],
    ["kubectl", "-n", "app", "rollout", "restart", "deploy/pokemon-fetcher"],
    ["bash", "-c", 'MSYS2_ARG_CONV_EXCL="*" aws logs describe-log-groups '
                  '--log-group-name-prefix /eks/pokemon-game/app --region eu-central-1'],
    ["bash", "-c", 'MSYS2_ARG_CONV_EXCL="*" aws logs describe-log-streams '
                  '--log-group-name /eks/pokemon-game/app --region eu-central-1 --max-items 10'],
    ["bash", "-c", 'MSYS2_ARG_CONV_EXCL="*" aws logs start-query '
                  '--region eu-central-1 '
                  '--log-group-names /eks/pokemon-game/app '
                  '--start-time $(( $(date +%s) - 900 )) '
                  '--end-time $(date +%s) '
                  '--query-string "fields @timestamp, @logStream, level, method, path, status | sort @timestamp desc | limit 20"']
]

for c in cmds:
    print(f"\n>>> Running: {' '.join(c)}\n")
    run(c, check=False)
