###############################################
# Argo CD namespace
###############################################
resource "kubernetes_namespace" "argocd" {
  metadata {
    name = "argocd"
    labels = {
      name              = "argocd"
      aws-observability = "enabled"
    }
  }
}

###############################################
# Fargate profile for Argo CD namespace
###############################################
resource "aws_eks_fargate_profile" "argocd" {
  cluster_name           = aws_eks_cluster.this.name
  fargate_profile_name   = "argocd"
  pod_execution_role_arn = aws_iam_role.fargate_pod_exec.arn

  subnet_ids = [
    aws_subnet.private["0"].id,
    aws_subnet.private["1"].id,
    aws_subnet.private["2"].id
  ]

  selector {
    namespace = "argocd"
  }

  tags = {
    Name = "pokemon-game-argocd-fargate"
  }

  depends_on = [
    aws_eks_cluster.this
  ]
}

###############################################
# Argo CD via Helm
###############################################
resource "helm_release" "argocd" {
  name      = "argocd"
  namespace = kubernetes_namespace.argocd.metadata[0].name

  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  version    = "7.7.10"

  create_namespace = false
  cleanup_on_fail  = true
  wait             = true
  timeout          = 600

  set {
    name  = "server.service.type"
    value = "ClusterIP"
  }

  set {
    name  = "server.ingress.enabled"
    value = "false"
  }

  set {
    name  = "server.extraArgs[0]"
    value = "--insecure"
  }

  set {
    name  = "controller.resources.requests.cpu"
    value = "100m"
  }

  set {
    name  = "controller.resources.requests.memory"
    value = "256Mi"
  }

  set {
    name  = "repoServer.resources.requests.cpu"
    value = "100m"
  }

  set {
    name  = "repoServer.resources.requests.memory"
    value = "256Mi"
  }

  set {
    name  = "server.resources.requests.cpu"
    value = "100m"
  }

  set {
    name  = "server.resources.requests.memory"
    value = "256Mi"
  }

  set {
    name  = "redis.resources.requests.cpu"
    value = "50m"
  }

  set {
    name  = "redis.resources.requests.memory"
    value = "128Mi"
  }

  depends_on = [
    aws_eks_fargate_profile.argocd,
    helm_release.alb_controller
  ]
}

###############################################
# Grant Argo CD controller cluster admin
###############################################
resource "kubernetes_cluster_role_binding" "argocd_controller_admin" {
  metadata {
    name = "argocd-application-controller-admin"
    labels = {
      "app.kubernetes.io/name" = "argocd"
    }
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "cluster-admin"
  }

  subject {
    kind      = "ServiceAccount"
    name      = "argocd-application-controller"
    namespace = kubernetes_namespace.argocd.metadata[0].name
  }

  depends_on = [
    helm_release.argocd
  ]
}

###############################################
# Argo CD Applications via argocd-apps Helm chart
###############################################
resource "helm_release" "argocd_apps" {
  name      = "argocd-apps"
  namespace = kubernetes_namespace.argocd.metadata[0].name

  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argocd-apps"
  version    = "1.6.2"

  create_namespace = false
  cleanup_on_fail  = true
  wait             = true
  timeout          = 600

  values = [
    yamlencode({
      applications = [
        {
          name      = "pokemon-game-app"
          namespace = kubernetes_namespace.argocd.metadata[0].name
          project   = "default"
          source = {
            repoURL        = "https://github.com/s1natex/Pokemon_Game"
            targetRevision = "main"
            path           = "k8s/app"
          }
          destination = {
            server    = "https://kubernetes.default.svc"
            namespace = "app"
          }
          syncPolicy = {
            automated = {
              prune    = true
              selfHeal = true
            }
            syncOptions = [
              "CreateNamespace=true",
              "ApplyOutOfSyncOnly=true"
            ]
          }
        }
      ]
    })
  ]

  depends_on = [
    helm_release.argocd,
    kubernetes_cluster_role_binding.argocd_controller_admin,
    helm_release.alb_controller
  ]
}

###############################################
# Internet facing ALB ingress for Argo CD UI
# TODO restrict inbound cidrs later
###############################################
resource "kubernetes_ingress_v1" "argocd_alb" {
  metadata {
    name      = "argocd-alb"
    namespace = kubernetes_namespace.argocd.metadata[0].name
    annotations = {
      "kubernetes.io/ingress.class"                = "alb"
      "alb.ingress.kubernetes.io/scheme"           = "internet-facing"
      "alb.ingress.kubernetes.io/target-type"      = "ip"
      "alb.ingress.kubernetes.io/healthcheck-path" = "/"
      "alb.ingress.kubernetes.io/listen-ports"     = "[{\"HTTP\":80}]"
      "alb.ingress.kubernetes.io/inbound-cidrs"    = "0.0.0.0/0"
    }
    labels = {
      "app.kubernetes.io/name" = "argocd"
    }
  }

  spec {
    rule {
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = "argocd-server"
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }

  depends_on = [
    helm_release.argocd,
    helm_release.alb_controller
  ]
}
