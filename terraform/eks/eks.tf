resource "aws_eks_cluster" "this" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks_cluster.arn

  vpc_config {
    endpoint_private_access = false
    endpoint_public_access  = true
    subnet_ids = concat(
      [for _, s in aws_subnet.public : s.id],
      [for _, s in aws_subnet.private : s.id]
    )
  }

  enabled_cluster_log_types = [
    "api",
    "audit",
    "authenticator",
    "controllerManager",
    "scheduler"
  ]

  tags = {
    Name    = var.cluster_name
    Project = var.project
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]
}

data "tls_certificate" "eks_oidc" {
  url = aws_eks_cluster.this.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "eks" {
  url = aws_eks_cluster.this.identity[0].oidc[0].issuer

  client_id_list = [
    "sts.amazonaws.com"
  ]

  thumbprint_list = [
    data.tls_certificate.eks_oidc.certificates[0].sha1_fingerprint
  ]
}

resource "aws_eks_fargate_profile" "app" {
  cluster_name           = aws_eks_cluster.this.name
  fargate_profile_name   = "app"
  pod_execution_role_arn = aws_iam_role.fargate_pod_exec.arn

  subnet_ids = [
    for _, s in aws_subnet.private : s.id
  ]

  selector {
    namespace = "app"
  }

  tags = {
    Name = "${var.project}-fp-app"
  }

  depends_on = [
    aws_eks_cluster.this
  ]
}

resource "aws_eks_fargate_profile" "system" {
  cluster_name           = aws_eks_cluster.this.name
  fargate_profile_name   = "system"
  pod_execution_role_arn = aws_iam_role.fargate_pod_exec.arn

  subnet_ids = [
    for _, s in aws_subnet.private : s.id
  ]

  selector {
    namespace = "kube-system"
  }

  tags = {
    Name = "${var.project}-fp-system"
  }

  depends_on = [
    aws_eks_cluster.this
  ]
}

