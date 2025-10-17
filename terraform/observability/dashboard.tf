resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project}-observability"
  dashboard_body = <<JSON
{
  "widgets": [
    {
      "type": "metric",
      "x": 0, "y": 0, "width": 12, "height": 6,
      "properties": {
        "title": "ALB RequestCount / 5xx",
        "metrics": [
          [ "AWS/ApplicationELB", "RequestCount", "LoadBalancer", "*", { "stat": "Sum" } ],
          [ "AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", "*", { "yAxis": "right", "stat": "Sum" } ]
        ],
        "period": 60,
        "region": "${var.region}",
        "view": "timeSeries",
        "stacked": false
      }
    },
    {
      "type": "metric",
      "x": 12, "y": 0, "width": 12, "height": 6,
      "properties": {
        "title": "ALB TargetResponseTime p50 p90 p99",
        "metrics": [
          [ "AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "*", { "stat": "p50" } ],
          [ "AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "*", { "stat": "p90" } ],
          [ "AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "*", { "stat": "p99" } ]
        ],
        "period": 60,
        "region": "${var.region}",
        "view": "timeSeries"
      }
    },
    {
      "type": "log",
      "x": 0, "y": 6, "width": 12, "height": 6,
      "properties": {
        "title": "Errors by service (last 1h)",
        "region": "${var.region}",
        "view": "table",
        "query": {
          "source": ["/eks/${var.project}/app"],
          "queryString": "fields @timestamp, @message, kubernetes.container_name as svc\\n| filter @message like /(?i)(error|exception)/\\n| stats count() as errors by svc\\n| sort errors desc"
        }
      }
    },
    {
      "type": "log",
      "x": 12, "y": 6, "width": 12, "height": 6,
      "properties": {
        "title": "Top HTTP paths (best-effort)",
        "region": "${var.region}",
        "view": "table",
        "query": {
          "source": ["/eks/${var.project}/app"],
          "queryString": "parse @message /(?i)(GET|POST|PUT|DELETE) (?<path>[^ \\\"\\n]+)/\\n| filter ispresent(path)\\n| stats count() as hits by path\\n| sort hits desc\\n| limit 10"
        }
      }
    },
    {
      "type": "log",
      "x": 0, "y": 12, "width": 12, "height": 6,
      "properties": {
        "title": "Recent error log lines",
        "region": "${var.region}",
        "view": "table",
        "query": {
          "source": ["/eks/${var.project}/app"],
          "queryString": "filter @message like /(?i)(error|exception)/\\n| fields @timestamp, kubernetes.container_name, @message\\n| sort @timestamp desc\\n| limit 50"
        }
      }
    },
    {
      "type": "log",
      "x": 12, "y": 12, "width": 12, "height": 6,
      "properties": {
        "title": "Frontend health hits",
        "region": "${var.region}",
        "view": "timeSeries",
        "query": {
          "source": ["/eks/${var.project}/app"],
          "queryString": "filter @message like /\\/healthz/\\n| stats count() as health_hits by bin(1m)"
        }
      }
    }
  ]
}
JSON
}
