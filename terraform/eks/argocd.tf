###############################################
# Argo CD Application: sync repo to cluster
###############################################
# Watches the repo and syncs /k8s/app to namespace 'app'
resource "kubernetes_manifest" "argocd_app_pokemon_game" {
  manifest = {
    "apiVersion" = "argoproj.io/v1alpha1"
    "kind"       = "Application"
    "metadata" = {
      "name"      = "pokemon-game-app"
      "namespace" = kubernetes_namespace.argocd.metadata[0].name
      "labels" = {
        "app.kubernetes.io/managed-by" = "terraform"
      }
    }
    "spec" = {
      "project" = "default"
      "source" = {
        "repoURL"        = "https://github.com/s1natex/Pokemon_Game"
        "path"           = "k8s/app"
        "targetRevision" = "main"
      }
      "destination" = {
        "server"    = "https://kubernetes.default.svc"
        "namespace" = "app"
      }
      "syncPolicy" = {
        "automated" = {
          "prune"    = true
          "selfHeal" = true
        }
        "syncOptions" = [
          "CreateNamespace=true",
          "ApplyOutOfSyncOnly=true"
        ]
      }
    }
  }

  depends_on = [
    helm_release.argocd,
    kubernetes_cluster_role_binding.argocd_controller_admin
  ]
}

###############################################
# Argo CD UI Ingress (ALB, internet-facing)
###############################################
# NOTE: IP allow list is set wide open for the interview demo
resource "kubernetes_manifest" "argocd_ingress" {
  manifest = {
    "apiVersion" = "networking.k8s.io/v1"
    "kind"       = "Ingress"
    "metadata" = {
      "name"      = "argocd-alb"
      "namespace" = kubernetes_namespace.argocd.metadata[0].name
      "annotations" = {
        "kubernetes.io/ingress.class"               = "alb"
        "alb.ingress.kubernetes.io/scheme"          = "internet-facing"
        "alb.ingress.kubernetes.io/target-type"     = "ip"
        "alb.ingress.kubernetes.io/healthcheck-path"= "/"
        "alb.ingress.kubernetes.io/listen-ports"    = "[{\"HTTP\":80}]"
        # restrict this CIDR allow list after demo
        "alb.ingress.kubernetes.io/inbound-cidrs"   = "0.0.0.0/0"
      }
      "labels" = {
        "app.kubernetes.io/name" = "argocd"
      }
    }
    "spec" = {
      "rules" = [
        {
          "http" = {
            "paths" = [
              {
                "path"     = "/"
                "pathType" = "Prefix"
                "backend" = {
                  "service" = {
                    "name" = "argocd-argocd-server"
                    "port" = { "number" = 80 }
                  }
                }
              }
            ]
          }
        }
      ]
    }
  }

  depends_on = [
    helm_release.argocd
  ]
}
