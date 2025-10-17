resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project}-observability"
  dashboard_body = <<JSON
{
  "widgets": [
    {
      "type": "metric",
      "x": 0,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "title": "ALB RequestCount / 5xx",
        "metrics": [
          [ "AWS/ApplicationELB", "RequestCount", "LoadBalancer", "${var.alb_arn_suffix}", { "stat": "Sum" } ],
          [ ".", "HTTPCode_Target_5XX_Count", ".", ".", { "yAxis": "right", "stat": "Sum" } ]
        ],
        "period": 60,
        "region": "${var.region}",
        "view": "timeSeries",
        "stacked": false
      }
    },
    {
      "type": "metric",
      "x": 12,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "title": "ALB TargetResponseTime p50 p90 p99",
        "metrics": [
          [ "AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "${var.alb_arn_suffix}", { "stat": "p50" } ],
          [ ".", "TargetResponseTime", ".", ".", { "stat": "p90" } ],
          [ ".", "TargetResponseTime", ".", ".", { "stat": "p99" } ]
        ],
        "period": 60,
        "region": "${var.region}",
        "view": "timeSeries"
      }
    },
    {
      "type": "log",
      "x": 0,
      "y": 6,
      "width": 12,
      "height": 6,
      "properties": {
        "title": "Errors by service (last 1h)",
        "region": "${var.region}",
        "view": "table",
        "query": "SOURCE '/eks/${var.project}/app' | fields @timestamp, @message, kubernetes.container_name as svc | filter @message like /(?i)(error|exception)/ | stats count() as errors by svc | sort errors desc"
      }
    },
    {
      "type": "log",
      "x": 12,
      "y": 6,
      "width": 12,
      "height": 6,
      "properties": {
        "title": "Top HTTP paths (best-effort)",
        "region": "${var.region}",
        "view": "table",
        "query": "SOURCE '/eks/${var.project}/app' | parse @message /(?i)(GET|POST|PUT|DELETE) (?<path>[^ \\\"\\n]+)/ | filter ispresent(path) | stats count() as hits by path | sort hits desc | limit 10"
      }
    },
    {
      "type": "log",
      "x": 0,
      "y": 12,
      "width": 12,
      "height": 6,
      "properties": {
        "title": "Recent error log lines",
        "region": "${var.region}",
        "view": "table",
        "query": "SOURCE '/eks/${var.project}/app' | filter @message like /(?i)(error|exception)/ | fields @timestamp, kubernetes.container_name, @message | sort @timestamp desc | limit 50"
      }
    },
    {
      "type": "log",
      "x": 12,
      "y": 12,
      "width": 12,
      "height": 6,
      "properties": {
        "title": "Frontend health hits",
        "region": "${var.region}",
        "view": "timeSeries",
        "query": "SOURCE '/eks/${var.project}/app' | filter @message like /\\/healthz/ | stats count() as health_hits by bin(1m)"
      }
    }
  ]
}
JSON
}
