resource "kubernetes_namespace" "aws_observability" {
  metadata {
    name = "aws-observability"
  }
}

resource "kubernetes_config_map" "aws_logging" {
  metadata {
    name      = "aws-logging"
    namespace = kubernetes_namespace.aws_observability.metadata[0].name
  }

  data = {
    "fluent-bit.conf" = <<EOT
[SERVICE]
    Flush        1
    Parsers_File parsers.conf

[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    multiline.parser  docker, cri
    Tag               kube.*
    Mem_Buf_Limit     512MB
    Skip_Long_Lines   On

[FILTER]
    Name                kubernetes
    Match               kube.*
    Kube_Tag_Prefix     kube.var.log.containers.
    Merge_Log           On
    Keep_Log            Off
    K8S-Logging.Parser  On
    K8S-Logging.Exclude Off

[OUTPUT]
    Name               cloudwatch_logs
    Match              kube.*
    region             ${var.region}
    log_group_name     /eks/${var.project}/app
    log_stream_prefix  from-eks-
    auto_create_group  true
    extra_user_agent   cwagent-fluent-bit

EOT

    "parsers.conf" = <<EOT
[PARSER]
    Name        docker
    Format      json
    Time_Key    time
    Time_Format %Y-%m-%dT%H:%M:%S.%L

[PARSER]
    Name        cri
    Format      regex
    Regex       ^(?<time>[^ ]+) (?<stream>stdout|stderr) (?<logtag>[^ ]*) (?<message>.*)$
    Time_Key    time
    Time_Format %Y-%m-%dT%H:%M:%S.%L%z
EOT
  }
}
