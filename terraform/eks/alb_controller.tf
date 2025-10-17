resource "aws_iam_role" "alb_controller" {
  name = "${var.project}-alb-controller"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.eks.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${replace(aws_iam_openid_connect_provider.eks.url, "https://", "")}:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "${replace(aws_iam_openid_connect_provider.eks.url, "https://", "")}:sub" = "system:serviceaccount:kube-system:aws-load-balancer-controller"
          }
        }
      }
    ]
  })
}

resource "aws_iam_policy" "alb_controller" {
  name   = "${var.project}-alb-controller-policy"
  policy = file("${path.module}/policies/aws-load-balancer-controller.json")
}

resource "aws_iam_role_policy_attachment" "alb_attach" {
  role       = aws_iam_role.alb_controller.name
  policy_arn = aws_iam_policy.alb_controller.arn
}

resource "kubernetes_service_account" "alb" {
  metadata {
    name      = "aws-load-balancer-controller"
    namespace = "kube-system"

    annotations = {
      "eks.amazonaws.com/role-arn" = aws_iam_role.alb_controller.arn
    }
  }
}

resource "helm_release" "alb_controller" {
  name             = "aws-load-balancer-controller"
  repository       = "https://aws.github.io/eks-charts"
  chart            = "aws-load-balancer-controller"
  namespace        = "kube-system"
  create_namespace = false

  values = [
    jsonencode({
      clusterName = var.cluster_name
      region      = var.region
      vpcId       = aws_vpc.main.id
      serviceAccount = {
        create = false
        name   = kubernetes_service_account.alb.metadata[0].name
      }
    })
  ]

  wait    = true
  atomic  = true
  timeout = 600

  depends_on = [
    aws_eks_cluster.this,
    aws_iam_role_policy_attachment.alb_attach,
    aws_eks_fargate_profile.system,
    aws_eks_fargate_profile.kube_system_alb
  ]
}

resource "aws_eks_fargate_profile" "kube_system_alb" {
  cluster_name           = aws_eks_cluster.this.name
  fargate_profile_name   = "kube-system-alb-controller"
  pod_execution_role_arn = aws_iam_role.fargate_pod_exec.arn

  subnet_ids = [
    aws_subnet.private["0"].id,
    aws_subnet.private["1"].id,
    aws_subnet.private["2"].id
  ]

  selector {
    namespace = "kube-system"
    labels = {
      "app.kubernetes.io/name" = "aws-load-balancer-controller"
    }
  }

  tags = {
    Name = "pokemon-game-kube-system-alb-fargate"
  }

  depends_on = [
    aws_eks_cluster.this
  ]
}
